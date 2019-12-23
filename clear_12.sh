for k in 'weekday' 'weekend'
    do
    rm -rf ${k}/PRED_TABLE/201912*
    for j in 'WT' 'TT'
        do
        for i in 'AVG' 'FILES' 'INT' 'RESULT'
            do
                rm -rf ${k}/${j}/${i}/201912*
            done
        done
    done

