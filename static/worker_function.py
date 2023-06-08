import time
import boto3



def work(buffer, iterations):
    import hashlib
    output = hashlib.sha512(buffer).digest()
    for i in range(iterations-1):
        output = hashlib.sha512(output).digest()
    return output

# Run the function
check_tasks_and_terminate()
