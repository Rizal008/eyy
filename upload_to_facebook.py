import requests
import os
import natsort
import time

# Ambil token dan ID halaman dari environment variables
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
PAGE_ID = os.getenv('PAGE_ID')
PHOTO_DIR = 'frames'  # Folder untuk postingan
COMMENT_PHOTO_DIR = 'raw'  # Folder untuk komentar
COMMENT_CAPTION = "Original image without subtitle"  # Caption tetap untuk komentar

def post_photo_to_facebook(photo_path, caption=""):
    url = f'https://graph.facebook.com/v12.0/{PAGE_ID}/photos'
    data = {'access_token': ACCESS_TOKEN, 'caption': caption}
    with open(photo_path, 'rb') as photo_file:
        files = {'source': photo_file}
        response = requests.post(url, data=data, files=files)
    return response.json()

def post_comment_with_photo(post_id, photo_path, message=""):
    url = f'https://graph.facebook.com/v12.0/{post_id}/comments'
    data = {'access_token': ACCESS_TOKEN, 'message': message}
    with open(photo_path, 'rb') as photo_file:
        files = {'source': photo_file}
        response = requests.post(url, data=data, files=files)
    return response.json()

def schedule_photos():
    if not os.path.exists(PHOTO_DIR):
        print(f"Error: Folder '{PHOTO_DIR}' tidak ditemukan.")
        return
    if not os.path.exists(COMMENT_PHOTO_DIR):
        print(f"Error: Folder '{COMMENT_PHOTO_DIR}' tidak ditemukan.")
        return

    # Ambil foto dari folder 'frames' dan 'raw'
    photos = natsort.natsorted([f for f in os.listdir(PHOTO_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
    comment_photos = natsort.natsorted([f for f in os.listdir(COMMENT_PHOTO_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
    
    photo_count = len(photos)
    comment_photo_count = len(comment_photos)
    
    if photo_count == 0:
        print(f"Tidak ada foto di folder '{PHOTO_DIR}'.")
        return
    if comment_photo_count == 0:
        print(f"Tidak ada foto di folder '{COMMENT_PHOTO_DIR}'.")
        return

    # Membagi foto menjadi batch 15 foto per jam
    for i in range(0, photo_count, 15):
        # Ambil 15 foto per batch dari folder 'frames'
        batch_photos = photos[i:i+15]
        
        for j, photo in enumerate(batch_photos):
            photo_path = os.path.join(PHOTO_DIR, photo)

            # Mengambil nama file tanpa ekstensi untuk dijadikan caption postingan
            filename_without_extension = os.path.splitext(photo)[0].replace('_', ' ').capitalize()

            # Upload foto utama ke Facebook
            response = post_photo_to_facebook(photo_path, caption=filename_without_extension)
            print(f'Uploaded {photo}: {response}')

            # Cek apakah ada gambar untuk komentar dari folder 'raw'
            if j < comment_photo_count:
                comment_photo = comment_photos[j]
                comment_photo_path = os.path.join(COMMENT_PHOTO_DIR, comment_photo)
                
                # Upload gambar versi tanpa subtitle ke komentar dengan caption tetap
                if 'id' in response:
                    post_id = response['id']
                    comment_response = post_comment_with_photo(post_id, comment_photo_path, message=COMMENT_CAPTION)
                    print(f'Commented with {comment_photo}: {comment_response}')
            
            # Tunggu 1 menit antar foto
            time.sleep(60)

        # Tunggu 1 jam sebelum melanjutkan ke batch berikutnya
        print("Waiting for 1 hour before the next batch of photos...")
        time.sleep(3600)

if __name__ == "__main__":
    schedule_photos()
