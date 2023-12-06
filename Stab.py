import string
import threading
from flask import Flask,jsonify,request
from flask_cors import CORS
import random
import time
import hashlib
app = Flask("Stab")
CORS(app)

# blockStatus
# Pending
# Committed
# Finalized
# Successed
# Failed

totalTxnList=[]
totalBlockList=[]
totalNodeList=[]
totalClientList=[]
BATCH_SIZE = 30
txnCount=1
blockCount=1  
nodeCount=1
clientCount=1
def generateTxn(blockNum,blockStatus,blockTimer):
    global txnCount,totalTxnList
    txnNum=txnCount
    txnHash=hashlib.sha256(("txn"+str(txnCount)).encode()).hexdigest()[:32]
    txnBelongBlock=blockNum
    txnBelongBatch=txnNum % BATCH_SIZE
    txnFrom=hashlib.sha256(("user"+str(random.randint(0,10000))).encode()).hexdigest()[:32]
    txnTo=hashlib.sha256(("user"+str(random.randint(0,10000))).encode()).hexdigest()[:32]
    if (txnNum % 5 == 0):
        txnOperation="Deposit"
    elif (txnNum % 5 == 1):
        txnOperation="Withdraw" 
    else :
        txnOperation="Transfer" 
    txnStatus=blockStatus
    txnTimeStamp=time.time()
    txnNonce=random.randint(0,100)
    txnValue=random.randint(0,3000)
    txnData=hashlib.sha256(("data"+str(txnValue)).encode()).hexdigest()[:32]
    txnTimer=blockTimer
    txnInfo=""
    txn_data = {
        "txnNum": txnNum,
        "txnStatus":txnStatus,
        "txnTimeStamp":txnTimeStamp,
        "txnHash": txnHash,
        "txnBelongBlock": txnBelongBlock,
        "txnBelongBatch": txnBelongBatch,
        "txnFrom": txnFrom,
        "txnTo": txnTo,
        "txnOperation": txnOperation,
        "txnNonce": txnNonce,
        "txnValue": txnValue,
        "txnData": txnData,
        "txnTimer":txnTimer,
        "txnInfo":txnInfo,
    }
    txnCount+=1
    totalTxnList.append(txn_data)
    return txn_data
  
def generateBlock():
    global blockCount,totalBlockList
    blockNum=blockCount
    blockHeight=blockNum + random.randint(0,20)
    
    if (blockHeight %4 ==0):
        blockStatus="Pending"
        blockTimer=[random.randint(0,100),0,0,0]
    if (blockHeight %4 ==1):    
        blockStatus="Committed"
        blockTimer=[random.randint(0,100),random.randint(0,100),0,0]
    if (blockHeight %4 ==2):    
        blockStatus="Finalized"
        blockTimer=[random.randint(0,100),random.randint(0,100),random.randint(0,100),0]
    if (blockHeight %4 ==3):
        if (random.randint(0,100) % 4 == 0):
            blockStatus="Failed"
            blockTimer=[random.randint(0,100),random.randint(0,100),random.randint(0,100),random.randint(0,100)]
        else:
            blockStatus="Successed"
            blockTimer=[random.randint(0,100),random.randint(0,100),random.randint(0,100),random.randint(0,100)]
    blockTxnNum=random.randint(10,20)
    blockTxnList=[]
    for i in range(0,blockTxnNum) :
        blockTxnList.append(generateTxn(blockNum,blockStatus,blockTimer))
    blockHash= hashlib.sha256(str(blockNum).encode()).hexdigest()[:32]
    blockParentHash=hashlib.sha256(str(blockNum-1).encode()).hexdigest()[:32]
    blockAge= time.time()
    blockInfo=""

    block_data = {
    "blockNum": blockNum,
    "blockHeight": blockHeight,
    "blockStatus": blockStatus,
    "blockTimer": blockTimer,
    "blockTxnNum": blockTxnNum,
    "blockTxnList": blockTxnList,
    "blockHash": blockHash,
    "blockParentHash": blockParentHash,
    "blockAge": blockAge,
    "blockInfo": blockInfo,
    }
    blockCount+=1
    totalBlockList.append(block_data)
    return block_data

def generateClient():
    global clientCount,totalClientList,totalTxnList
    clientNum=clientCount
    clientName="client"+str(clientNum)
    clientAddress= clientCount
    # hashlib.sha256("client"+str(clientCount).encode()).hexdigest()[:32]
    clientCommitedNonce=random.randint(0,100)
    clientVerifiedNonce=random.randint(clientCommitedNonce-random.randint(0,clientCommitedNonce),clientCommitedNonce)
    clientPublishedTxnNum=clientCommitedNonce
    clientPublishedTxnList=[]
    for i in range(0,clientPublishedTxnNum):
        clientPublishedTxnList.append(totalTxnList[random.randint(0,len(totalTxnList)-1)])
    clientAssetList=[]
    clientAssetList.append(["USD",random.randint(0,10000)])
    clientAssetList.append(["YUAN",random.randint(0,10000)])
    clientAssetList.append(["ERU",random.randint(0,10000)])
    client_data={
        "clientNum":clientNum,
        "clientName":clientName,
        "clientAddress":clientAddress,
        "clientCommitedNonce":clientCommitedNonce,
        "clientVerifiedNonce":clientVerifiedNonce,
        "clientPublishedTxnNum":clientPublishedTxnNum,
        "clientPublishedTxnList":clientPublishedTxnList,
        "clientAssetList":clientAssetList,
    }
    clientCount+=1
    totalClientList.append(client_data)
    return client_data


# 暂时节点模拟在这里
def generateNode():
    global nodeCount,totalNodeList
    nodeNum = nodeCount
    nodeName = "Node" + str(nodeNum)
    if random.randint(0, 30) == 0:
        nodeStatus = "Crashed"
    else:
        nodeStatus = "Operating"
    if random.randint(0, 10) == 0:
        nodeMode = "Byzantine"
    else:
        nodeMode = "Correct"
    nodePublicKey = hashlib.sha256(("nodePub" + str(random.randint(0, 10000))).encode()).hexdigest()[:32]
    nodePrivateKey = hashlib.sha256(("nodePri" + str(random.randint(0, 10000))).encode()).hexdigest()[:32]
    nodeAddress = ".".join(str(random.randint(90, 191)) for _ in range(4))
    nodeWidth = str(random.randint(30, 300)) + "GB/S"
    nodeCurrentEpoch = str(random.randint(30, 300))
    if random.randint(0, 3) == 0:
        nodeCurrentPhase = "Committing"
    else:
        nodeCurrentPhase = "Preparing"
    nodeCurrentCapacity = str(random.randint(30, 300)) + "GB"
    nodeCurrentBlockHeight = str(random.randint(3, 30))
    #nodeLocalLog = [totalBlockList[random.randint(0, len(totalBlockList) - 1)] for _ in range(nodeCurrentBlockHeight)]
    node_data = {
        "nodeNum":nodeNum,
        "nodeName": nodeName,
        "nodeStatus": nodeStatus,
        "nodeMode": nodeMode,
        "nodePublicKey": nodePublicKey,
        "nodePrivateKey": nodePrivateKey,
        "nodeAddress": nodeAddress,
        "nodeWidth": nodeWidth,
        "nodeCurrentEpoch": nodeCurrentEpoch,
        "nodeCurrentPhase": nodeCurrentPhase,
        "nodeCurrentCapacity": nodeCurrentCapacity,
        "nodeCurrentBlockHeight": nodeCurrentBlockHeight,
        #"nodeLocalLog": nodeLocalLog,
    }
    nodeCount+=1
    totalNodeList.append(node_data)
    return node_data

chainCodeCount=2


for i in range(0,300):
    generateBlock()
for i in range(0,30):
    generateClient()
for i in range(0,7):
    generateNode()

def generate_block_periodically():
    while True:
        times=random.randint(0,30)
        for i in range(0,times):
            generateBlock()
            time.sleep(1)

thread1 = threading.Thread(target=generate_block_periodically)
thread1.start()


def generate_node_running_info_periodically():
    while True:
        times=random.randint(0,3)
        for i in range(0,times):
            select=random.randint(0,len(totalNodeList)-1)
            totalNodeList[select]['nodeCurrentEpoch']+=1
            if(random.randint(0,3)==0):
                totalNodeList[select]["nodeCurrentPhase"]="Committing"
            else:
                totalNodeList[select]["nodeCurrentPhase"]="Preparing"
            totalNodeList[select]['nodeCurrentEpoch']+=0.1
            totalNodeList[select]["nodeCurrentBlockHeight"]+=random.randint(0,5)
            #totalNodeList[select]['nodeLocalLog'].append([totalBlockList[random.randint(0, len(totalBlockList) - 1)] for _ in range(0,totalNodeList[select]["nodeCurrentBlockHeight"]-len(totalNodeList[select]['nodeLocalLog']))])

thread2 = threading.Thread(target=generate_node_running_info_periodically)
thread2.start()


@app.route('/normalInfo', methods=['GET'])
def returnnormalInfo():
    blockNum = totalBlockList.__len__()
    txnNum = totalTxnList.__len__()
    nodeNum = nodeCount
    chainCodeNum = chainCodeCount
    data = {
        "blockNum": blockNum,
        "txnNum": txnNum,
        "nodeNum": nodeNum,
        "chainCodeNum": chainCodeNum
    }
    return jsonify(data)




@app.route('/latestBlock', methods=['GET'])
def returnBlockInfo():
    latestBlock = totalBlockList[-10:][::-1] 
    return jsonify(latestBlock)

@app.route('/LatestTxn', methods=['GET'])
def returnTxnInfo():
    latestTxn = totalTxnList[-30:][::-1] 
    return jsonify(latestTxn)

@app.route('/AllBlock',methods=['GET'])
def returnAllBlockInfo():
    return jsonify(totalBlockList[::-1] )

@app.route('/AllTxn',methods=['GET'])
def returnAllTxnInfo():
    return jsonify(totalTxnList[::-1] )

@app.route('/AllNode',methods=['GET'])
def returnNodeInfo():
    return jsonify(totalNodeList)

@app.route('/GetClient',methods=['POST'])
def getOneClient():
    if request.method == 'POST':
        clientAddress = request.form.get("clientAddress")
        print(clientAddress)
        return totalClientList[int(clientAddress)]
    
@app.route('/SubmitTxn',methods=['POST'])
def receivingOneTxn():
    if request.method == 'POST':
        form_data = request.form.to_dict()
        for key, value in form_data.items():
            print(f"{key}: {value}")
        return 'Success'
    
    
if __name__ == '__main__':
    app.run(host='localhost', port=8000)

