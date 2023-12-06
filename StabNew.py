import math
import string
import threading
import random
import time
import hashlib
from jose import jwt
from datetime import datetime
from flask import Flask,jsonify,request
from flask_cors import CORS

userDict = {}
nodeList = []
txnList = []
blockList = []

def generateUser(email,password,_type,privateKey):
    user_info = {
        'userId':len(userDict),
        'userEmail': email,
        'userPassword': password,
        'userAddress': '',
        'userType': _type,
        'userPrivateKey':privateKey,
        # 从这里开始 以上为静态信息 以下为动态信息(需要维护的信息)
        'userCommittedNonce':0,
        'userVerifiedNonce':0,
        'userBalance':2000,
        'userAssetList':[],
    }
    userDict[email] = user_info
    return user_info

def generateNode(name,mode,publicKey,privateKey,address,config):
    node_info = {
        'nodeId':len(nodeList),
        'nodeName':name,
        'nodeMode':mode,
        'nodePublicKey':publicKey,
        'nodePrivateKey':privateKey,
        'nodeAddress':address,
        'nodeConfig': config,
        # 从这里开始 以上为静态信息 以下为动态信息(需要维护的信息)
        'nodeStatus': 'Running',
        'nodeCurrentEpoch':0,
        'nodeCurrentPhase':0,
        'nodeCurrentBlockHeight':0,
        'nodeLocalLog':[],
    }
    nodeList.append(node_info)
    return node_info

def generateTxn(_from,_to,operation,nonce,value,data,info):
    txn_info={
        'txnFrom':_from,
        'txnTo':_to,
        'txnOperation': operation,
        'txnNonce':nonce,
        'txnValue':value,
        'txnData':data,
        'txnInfo':info,
        'txnId':len(txnList),
        'txnHash':'',
        'txnStamp': math.floor(datetime.now().timestamp() / 1000),        
        # 从这里开始 以上为静态信息 以下为动态信息(需要维护的信息)
        'txnStatus':'Pending',
        'txnBelongBlock':None,
        'txnBelongBatch':None,
        'txnTimer':[math.floor(datetime.now().timestamp() / 1000),0,0,0]
    }
    txnList.append(txn_info)
    return txn_info

def spamTxn(low,high,txnCount):
    for i in range(0,txnCount):
        _from = str(random.randint(low,high))+'@example.com'
        _to = str(random.randint(low,high))+'@example.com'            
        nonce = userDict[_from]['userCommittedNonce']
        userDict[_from]['userCommittedNonce']+=1
        if random.randint(0,10) % 5 == 0:
            generateTxn(_from,_from,'mint',nonce, random.randint(0,10) ,None,None)
        else:
            generateTxn(_from,_to,'transfer',nonce, random.randint(0,10) ,None,None)


def executeTxn(txn):
    _from = userDict[txn['txnFrom']]
    _to = userDict[txn['txnTo']]
    operation = txn['txnOperation']
    nonce =txn['txnNonce']
    _value = txn['txnValue']
    data = txn['txnData']
    info = txn['txnInfo']

    _from['userVerifiedNonce']+=1
    if operation=='mint':
        _from['userBalance']+=_value
        if data:
            for key,value in data.items():
                if _from['userAssetList'][key] ==None:
                    _from['userAssetList'][key]=0
                _from['userAssetList'][key] += value

    if operation=='transfer':
        _from['userBalance']-=_value
        _to['userBalance']+=_value
        if data:
            for key,value in data.items():
                if _from['userAssetList'][key] ==None:
                    _from['userAssetList'][key]=0
                _from['userAssetList'][key] += value
                _to['userAssetList'][key] -= value


# 交易足够后成Batch Batch形成后开始打包成块，这里直接忽略Batch 用MOD 50识别 每25txn为一block 每5block为一batch
# 这里模拟处理块 假定以下规则
# 出块速度为每8秒一块 ，即每五秒调用一次generateBlock block初始化 更新txn状态 block batch 
# 其余各个间隔为2秒一次，即每二秒调用一次processBlock对一个未出结果的块block推进1 进度
# Pending->Committed 更新节点状态Epoch 重置Phase 更新txn状态 status timer 更新block 状态 status timer 
# Committed->Phase1 更新节点状态Phase
# Phase1->Phase2 更新节点状态Phase 
# Phase2->Finalized 更新节点状态Phase Log BlockHeight   更新txn状态 status timer 更新block状态 status timer
# Finalized->Success/Fail 模拟交易执行 更新user状态 from的v-nonce from\to的balance和asset list 更新txn状态 status和timer

BLOCK_SIZE = 25
BATCH_SIZE = 50
block_genesis={
    "blockId":0,
    "blockHeight":0,
    "blockParentHash":'',
    "blockAge": math.floor(datetime.now().timestamp() / 1000),
    'blockBelongBatch':0, 
    "blockHash": '',
    "blockStatus": 'Success',
    "blockTimer": [0,0,0,0],
    "blockTxnNum": None,
    "blockTxnList": [],
    "blockInfo": '',
}
blockList.append(block_genesis)
def generateBlock():
    block_info={
    "blockId": len(blockList),
    "blockHeight": len(blockList),
    "blockParentHash": blockList[len(blockList)-1]['blockHash'],
    "blockAge": math.floor(datetime.now().timestamp() / 1000),
    'blockBelongBatch':int(len(blockList)/2),    
    "blockHash": '',
    # 从这里开始 以上为静态信息 以下为动态信息(需要维护的信息)
    "blockStatus": 'Pending',    
    "blockTimer": [math.floor(datetime.now().timestamp() / 1000),0,0,0],
    "blockTxnNum": None,
    "blockTxnList": [],
    "blockInfo": '',
    }
    count = 0
    for txn in txnList:
        if txn['txnStatus'] == 'Pending' and (not txn['txnBelongBlock']):
            count += 1
            block_info['blockTxnList'].append(txn)
        if count == BLOCK_SIZE:
            break
    block_info['blockTxnNum']= len(block_info['blockTxnList'])
    for txn in block_info['blockTxnList']:
        txn['txnBelongBlock']=block_info['blockId']
        txn['txnBelongBatch']=block_info['blockBelongBatch']
    blockList.append(block_info)
    return block_info

def processBlock():
    for block in blockList:
        if block["blockStatus"] == 'Pending':
            print("Block commit:",block['blockId'])
            block["blockStatus"] = 'Committed'
            block['blockTimer'][1] = math.floor(datetime.now().timestamp() / 1000)
            for node in nodeList:
                node['nodeCurrentEpoch']+=1
                node['nodeCurrentPhase']=0
            for txn in block['blockTxnList']:
                txn['txnStatus'] = 'Committed'
                txn['txnTimer'][1]= math.floor(datetime.now().timestamp() / 1000)
            break
        if block['blockStatus'] == 'Committed' and nodeList[0]['nodeCurrentPhase']==0:
            print("Block p1:",block['blockId'])
            for node in nodeList:
                node['nodeCurrentPhase'] +=1
            break
        if block['blockStatus'] == 'Committed' and nodeList[0]['nodeCurrentPhase']==1:
            print("Block p2:",block['blockId'])
            for node in nodeList:
                node['nodeCurrentPhase'] +=1
            break
        if block['blockStatus'] == 'Committed' and nodeList[0]['nodeCurrentPhase']==2:
            print("Block finalized:",block['blockId'])
            block["blockStatus"] = 'Finalized'
            block['blockTimer'][2] = math.floor(datetime.now().timestamp() / 1000)
            for txn in block['blockTxnList']:
                txn['txnStatus'] = 'Finalized'
                txn['txnTimer'][2]= math.floor(datetime.now().timestamp() / 1000)
            for node in nodeList:
                node['nodeCurrentPhase'] +=1
                node['nodeCurrentBlockHeight'] +=1
                node['nodeLocalLog'].append(block)  
            break     
        if block['blockStatus'] == 'Finalized':
            print("Block sealed:",block['blockId'])
            if random.randint(0,100) % 50 != 0:
                block["blockStatus"] = 'Success'
                block['blockTimer'][3] = math.floor(datetime.now().timestamp() / 1000)
                for txn in block['blockTxnList']:
                    txn['txnStatus'] = 'Success'
                    txn['txnTimer'][3]= math.floor(datetime.now().timestamp() / 1000)
                    executeTxn(txn)
            else:
                block["blockStatus"] = 'Failed'
                block['blockTimer'][3] = math.floor(datetime.now().timestamp() / 1000)
                for txn in block['blockTxnList']:
                    txn['txnStatus'] = 'Failed'
                    txn['txnTimer'][3]= math.floor(datetime.now().timestamp() / 1000)
            break
                    

# 总而言之需要先随机生成一些数据...
class InitGen:
    @staticmethod
    def generateInitUser(userInitCount):
        for i in range(0,userInitCount):
            email= str(i) + '@example.com'
            password=str(i)
            _type = 0
            privateKey = str(i)
            generateUser(email=email,password=password,_type=_type,privateKey=privateKey)
    @staticmethod
    def generateInitNode(nodeInitCount):
        for i in range(0,nodeInitCount):
            name= 'Node' + str(i)
            mode= 'Correct'
            publicKey=''
            privateKey=''
            address=''
            config={
                'nodeWidth':1000,
                'nodeCapacity':1000,
            }
            generateNode(name=name,mode=mode,publicKey=publicKey,privateKey=privateKey,address=address,config=config)
    @staticmethod
    def generateInitTxn(txnInitCount):
        for i in range(0,len(userDict)-1):
            nonce = userDict[str(i)+'@example.com']['userCommittedNonce']
            userDict[str(i)+'@example.com']['userCommittedNonce']+=1
            generateTxn(str(i)+'@example.com',str(i)+'@example.com','mint',nonce, 10000 ,None,None)
        for i in range(0,txnInitCount):
            _from = str(random.randint(0,len(userDict)-1))+'@example.com'
            _to = str(random.randint(0,len(userDict)-1))+'@example.com'            
            nonce = userDict[_from]['userCommittedNonce']
            userDict[_from]['userCommittedNonce']+=1

            if random.randint(0,10) % 5 == 0:
                generateTxn(_from,_from,'mint',nonce, random.randint(0,10) ,None,None)
            else:
                generateTxn(_from,_to,'transfer',nonce, random.randint(0,10) ,None,None)

InitGen.generateInitNode(5)
InitGen.generateInitUser(10)
InitGen.generateInitTxn(100)

# 然后例行的模拟一些数据
def makeBlock():
    while True:
        spamTxn(0,9,random.randint(10,30))
        generateBlock() 
        time.sleep(8)   
def proBlock():
    while True:
        processBlock()
        time.sleep(2)

makeBlockThread = threading.Thread(target=makeBlock)
makeBlockThread.start()

proBlockThread = threading.Thread(target=proBlock)
proBlockThread.start()

# ------------------------------------------------------以上为模拟执行部分，之后为接口部分--------------------------------------------------------------

app = Flask(__name__)
CORS(app)

## 模拟登录
# @TODO 将token改为鉴权应用到接口上
SECRET_KEY = "your-secret-key"

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if email in userDict and userDict[email]['userPassword'] == password:
            token = jwt.encode({"email": email}, SECRET_KEY, algorithm="HS256")
            userDict[email]['userToken']=token
            return jsonify({"token": token}), 200
        else:
            print(userDict)
            return jsonify({"error": "Invalid credentials"}), 401
    

@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if email in userDict :
            return jsonify({"error": "User Exist"}), 401
        
        generateUser(email=email,password=password,type=1,privateKey="")

        token = jwt.encode({"email": email}, SECRET_KEY, algorithm="HS256")
        userDict[email]['userToken']=token
        
        return jsonify({"token": token}), 200
    

# 总览面板数据一
@app.route('/normalInfo', methods=['GET'])
def returnnormalInfo():
    blockNum = len(blockList)
    txnNum = len(txnList)
    nodeNum = len(nodeList)
    chainCodeNum = 2
    data = {
        "blockNum": blockNum,
        "txnNum": txnNum,
        "nodeNum": nodeNum,
        "chainCodeNum": chainCodeNum
    }
    return jsonify(data)

## 总览面板数据二
TXN_MAX_LANTENCY = 200
TXN_MIN_LANTENCY = 20
TXN_MIN_THROUGHTOUT = 100
TXN_MAX_THROUGHTOUT = 300
BLOCK_MAX_LANTENCY = 1000
BLOCK_MIN_LANTENCY = 200
BLOCK_MIN_THROUGHTOUT = 10
BLOCK_MAX_THROUGHTOUT = 30

# @TODO 改为模拟数据
@app.route('/runningInfo', methods=['GET'])
def returnRunningInfo():
    blockLatencyAvg = random.randint(BLOCK_MIN_LANTENCY,BLOCK_MAX_LANTENCY)
    blockLatency = random.randint(blockLatencyAvg-50,blockLatencyAvg+50)
    blockLatencyMax = BLOCK_MAX_LANTENCY
    blockThroughputAvg = random.randint(BLOCK_MIN_THROUGHTOUT,BLOCK_MAX_THROUGHTOUT)
    blockThroughput = random.randint( blockThroughputAvg-3, blockThroughputAvg+3)
    blockThroughputMax = BLOCK_MAX_THROUGHTOUT

    txnLatencyAvg = random.randint(TXN_MIN_LANTENCY,TXN_MAX_LANTENCY)
    txnLatency = random.randint(txnLatencyAvg-5,txnLatencyAvg+5)
    txnLatencyMax = TXN_MAX_LANTENCY

    
    txnThroughputAvg = random.randint(TXN_MIN_THROUGHTOUT,TXN_MAX_THROUGHTOUT)
    txnThroughput = random.randint( txnThroughputAvg-30, txnThroughputAvg+30)
    txnThroughputMax = TXN_MAX_THROUGHTOUT

    data = {
        "blockLatency" : blockLatency,
        "blockLatencyAvg" : blockLatencyAvg,
        "blockLatencyMax" : blockLatencyMax,
        "blockThroughput" : blockThroughput,
        "blockThroughputAvg" : blockThroughputAvg,
        "blockThroughputMax" : blockThroughputMax,
        "txnLatency" : txnLatency,
        "txnLatencyAvg" : txnLatencyAvg,
        "txnLatencyMax" : txnLatencyMax,
        "txnThroughput" : txnThroughput,
        "txnThroughputAvg" : txnThroughputAvg,
        "txnThroughputMax" : txnThroughputMax,
    }
    return jsonify(data)

@app.route('/latestBlock', methods=['GET'])
def returnBlockInfo():
    latestBlock = blockList[-10:][::-1] 
    return jsonify(latestBlock)


    
if __name__ == '__main__':
    app.run(host='localhost', port=8000)