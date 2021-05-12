# Code for downloading HowTo100M videos
 
1. Downloading CSVs and JSONs of HowTo100M dataset from: https://www.di.ens.fr/willow/research/howto100m/. After
 extracting the zip file, we can obtain a text file containing list of dataset's video-urls:howto100m_videos.txt

2. Fill the form provided by the author to get the `user_name` and `password` for mirror link downloading.

3. Download videos by commands
```python
python download.py  --video_list_file path/to/howto100m_videos.txt --user_name user_name --password your_pass_word 
--num_threads 20
```  
