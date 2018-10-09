import os, uuid, sys
from azure.storage.blob import BlockBlobService, PublicAccess



def run_sample():
    try:
        block_blob_service = BlockBlobService(account_name='rvsafeimages', account_key='391TMmlvDdRWu+AsNX+ZMl1i233YQfP5dxo/xhMrPm22KtwWwwMmM9vFAJpJHrGXyBrTW4OoAInjHnby9Couug==')

        container_name ='imagescontainer'
        block_blob_service.create_container(container_name)

        # Set the permission so the blobs are public.
        block_blob_service.set_container_acl(container_name, public_access=PublicAccess.Container)

        # Create a file in Documents to test the upload and download.
        local_path=os.path.expanduser("/home/yatish/Desktop/azuretest/")
        #local_file_name ="QuickStart_" + str(uuid.uuid4()) + ".jpg"
        local_file_name = 'jpeg.jpg'
        full_path_to_file =os.path.join(local_path, local_file_name)

        # Write text to the file.
        # file = open(full_path_to_file,  'w')
        # file.write("Hello, World!")
        # file.close()

        

        print("Temp file = " + '/home/yatish/Desktop/azuretest/jpeg.jpg')
        print("\nUploading to Blob storage as blob" + local_file_name)

        # Upload the created file, use local_file_name for the blob name
        block_blob_service.create_blob_from_path(container_name, local_file_name, full_path_to_file)

        # List the blobs in the container
        print("\nList blobs in the container")
        generator = block_blob_service.list_blobs(container_name)
        for blob in generator:
            print("\t Blob name: " + blob.name)

        # Download the blob(s).
        # Add '_DOWNLOADED' as prefix to '.jpg' so you can see both files in Documents.
        full_path_to_file2 = os.path.join(local_path, str.replace(local_file_name ,'.jpg', '_DOWNLOADED.jpg'))
        print("\nDownloading blob to " + full_path_to_file2)
        block_blob_service.get_blob_to_path(container_name, local_file_name, full_path_to_file2)

        sys.stdout.write("Sample finished running. When you hit <any key>, the sample will be deleted and the sample "
                         "application will exit.")
        sys.stdout.flush()
        input()

        # Clean up resources. This includes the container and the temp files
        block_blob_service.delete_container(container_name)
        os.remove(full_path_to_file)
        os.remove(full_path_to_file2)
    except Exception as e:
        print(e)


# Main method.
if __name__ == '__main__':
    run_sample()



