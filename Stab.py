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
TXN_MAX_LANTENCY = 200
TXN_MIN_LANTENCY = 20
TXN_MIN_THROUGHTOUT = 100
TXN_MAX_THROUGHTOUT = 300
BLOCK_MAX_LANTENCY = 1000
BLOCK_MIN_LANTENCY = 200
BLOCK_MIN_THROUGHTOUT = 10
BLOCK_MAX_THROUGHTOUT = 30
totalTxnList=[]
totalBlockList=[]
totalNodeList=[]
BATCH_SIZE = 30
txnCount=1
blockCount=1  
nodeCount=1
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

# 暂时节点模拟在这里
nodeCount=10
def generateNode():
    global nodeCount,totalNodeList
    nodeNum=nodeCount
    nodeName="Node"+str(nodeNum)
    node_data={
        "nodeNum":nodeNum,
        "nodeName":nodeName,
    }
    nodeCount+=1
    totalNodeList.append(node_data)
    return node_data


chainCodeCount=2


for i in range(0,300):
    generateBlock()
for i in range(0,nodeCount):
    generateNode()

def generate_block_periodically():
    while True:
        times=random.randint(0,30)
        for i in range(0,times):
            generateBlock()
            time.sleep(1)

thread = threading.Thread(target=generate_block_periodically)
thread.start()



@app.route('/NormalInfo', methods=['GET'])
def returnNormalInfo():
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

@app.route('/RunningInfo', methods=['GET'])
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


@app.route('/LatestBlock', methods=['GET'])
def returnBlockInfo():
    latestBlock = totalBlockList[-10:][::-1] 
    return jsonify(latestBlock)

@app.route('/LatestTxn', methods=['GET'])
def returnTxnInfo():
    latestTxn = totalTxnList[-10:][::-1] 
    return jsonify(latestTxn)

@app.route('/AllBlock',methods=['GET'])
def returnAllBlockInfo():
    return jsonify(totalBlockList)[::-1] 

@app.route('/AllTxn',methods=['GET'])
def returnAllTxnInfo():
    return jsonify(totalTxnList)[::-1] 

@app.route('/AllNode',methods=['GET'])
def returnNodeInfo():
    return jsonify(totalNodeList)



@app.route('/SubmittingOneTxn',methods=['POST'])
def receivingOneTxn():
    if request.method == 'POST':
        txnNum = request.form.get('txnNum')
        from_value = request.form.get('from')
        to_value = request.form.get('to')
        amount = request.form.get('amount')
        node = request.form.get('node')

        # 打印表单数据
        print(f"事务编号: {txnNum}")
        print(f"来自: {from_value}")
        print(f"发往: {to_value}")
        print(f"交易额度: {amount}")
        print(f"发送节点: {node}")

        # 在这里可以进行进一步的处理

        return 'Success'

if __name__ == '__main__':
    app.run(host='localhost', port=8000)

