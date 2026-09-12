import os

def delete_empty_images(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            path = os.path.join(root, file)
            size = os.path.getsize(path)
            if size == 16:
                print(f"Deleting empty image {path}")
                os.remove(path)

delete_empty_images(r"d:\Projects\Nova\backend\assets")
