from IBMQuantumExperience import IBMQuantumExperience

# production
#api = IBMQuantumExperience("753513bb53f2a908ced00145a4b3903182afc1344eed1411770c281ce22cbc3a5660bed36a5aeb52e5775a67ba4d2c51218c7d5248b4f40cafc1ebc86e85b8c7", {'url': 'https://qcwi-mirror.mybluemix.net/api'})
#api = IBMQuantumExperience("b1d738b69dd8f0936687352b63a82397b38bdd65ae7629fb4c00ff5036e11641641ce2247fb7fb9722dc00ec3829622dd553e6ed07fa896dd01daec186ba1c63") # "demo@demo.com", "demo1234QBITS"
#api = IBMQuantumExperience("753513bb53f2a908ced00145a4b3903182afc1344eed1411770c281ce22cbc3a5660bed36a5aeb52e5775a67ba4d2c51218c7d5248b4f40cafc1ebc86e85b8c7")

qasm = 'IBMQASM 2.0;\n\ninclude "qelib1.inc";\nqreg q[5];\ncreg c[5];\nx q[0];\ncx q[0],q[2];\nmeasure q[0] -> c[0];\nmeasure q[2] -> c[1];\n'
#qasm = 'include \"qelib1.inc\";\nqreg q[5];\ncreg c[5];\nh q[0];\nh q[2];\ns q[2];\n'

# develop
api = IBMQuantumExperience("9c036ee46287a9a1655eb53dfa31144f0d83d6a27d628ae5effce3876a9166c016747765c69431fcee2b37ef4f08647451ea226f001813a5338676b405c6c527", {'url': 'https://qcwi-develop.mybluemix.net/api'})
qasm1 = {"qasm": 'IBMQASM 2.0;\n\ninclude "qelib1.inc";\nqreg q[5];\ncreg c[5];\nh q[0];\ncx q[0],q[2];\nmeasure q[0] -> c[0];\nmeasure q[2] -> c[1];\n'}
qasm2 = {"qasm": 'IBMQASM 2.0;\n\ninclude "qelib1.inc";\nqreg q[5];\ncreg c[5];\nx q[0];\ncx q[0],q[2];\nmeasure q[0] -> c[0];\nmeasure q[2] -> c[1];\n'}
qasm3 = {"qasm": 'IBMQASM 2.0;\n\ninclude "qelib1.inc";\nqreg q[5];\ncreg c[5];\ny q[0];\ncx q[0],q[2];\nmeasure q[0] -> c[0];\nmeasure q[2] -> c[1];\n'}
qasms = [qasm1,qasm2,qasm3]
#result = api.runExperiment(qasm, 'sim', 1)
#result = api.runJob(qasms)
#print(result)
#print('*****************************')
#job = api.getJob('9de64f58316db3eb6db6da53bf7135ff')
#print(job)
#codeid = result['idCode']
#code = api.getImageCode(codeid)
#print(code)

'''codes = api.getLastCodes()
for c in codes:
    for execution in c['executions']:
        print(execution['status'])'''