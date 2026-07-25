from ib_insync import *

print("Connecting...")

ib = IB()

ib.connect(
    "127.0.0.1",
    7497,
    clientId=1
)

print("Connected!")
print()

print("Accounts:")
print(ib.managedAccounts())

print()

account_values = ib.accountSummary()

for item in account_values[:10]:
    print(item)

ib.disconnect()