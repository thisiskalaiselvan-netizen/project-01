from google.cloud import storage

client = storage.Client()

print("Buckets available:")
for bucket in client.list_buckets():
    print(bucket.name)
