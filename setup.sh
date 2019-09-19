python setup.py

filename="models.zip"
fileid="1OH8ZYoQyaMfuLSYe2GpqmnyYOAm5VL55"
query=`curl -c ./cookie.txt -s -L "https://drive.google.com/uc?export=download&id=${fileid}" | pup 'a#uc-download-link attr{href}' | sed -e 's/amp;//g'`
curl -b ./cookie.txt -L -o ${filename} "https://drive.google.com${query}"
rm -rf ./cookie.txt

unzip models.zip

for k in 'weekday' 'weekend'
    do
    for j in 'WT' 'TT'
        do
        for i in 1 2 3
            do
            mv ./models/${k}_${j}_model_${i}.h5 ./${k}/${j}/MODELS/model_${i}.h5
            done
        done
    done

rm -rf ./models
rm -rf ./models.zip


filename="5413_data.zip"
fileid="1tivkptPEIxZ6TWXLQOFzTAF9qqRcpzXL"
query=`curl -c ./cookie.txt -s -L "https://drive.google.com/uc?export=download&id=${fileid}" | pup 'a#uc-download-link attr{href}' | sed -e 's/amp;//g'`
curl -b ./cookie.txt -L -o ${filename} "https://drive.google.com${query}"
rm -rf ./cookie.txt

unzip 5413_data.zip -d ./xlsFiles

rm -rf 5413_data.zip

filename="transactionHistory.xls"
fileid="172gk_VfvhB1CQT3iGZDMk4ZLAhmiPp0i"

curl -L -o ${filename} "https://drive.google.com/uc?export=download&id=${fileid}"

python parseCardData.py ${filename}

python uploadProcess.py
python avgProcess.py

