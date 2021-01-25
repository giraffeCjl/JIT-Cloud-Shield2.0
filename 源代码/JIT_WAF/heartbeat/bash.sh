#!/bin/bash
#正则匹配参数信息
update_one_second(){
    memory=`cat /proc/meminfo |grep MemFree | awk  -F ' ' '{print$2}'`
    tcp=`netstat -nat|grep -i "80"|wc -l`
}
#获取上一秒参数
last(){ 
    update_one_second
    memory_last=$memory
    tcp_last=$tcp
}
#获取当前时间参数
now(){
    update_one_second
    memory_now=$memory
    tcp_now=$tcp
}
#算参数的梯度
accelerated(){
    last
    sleep 1s
    now
    memory_a=`expr $memory_last - $memory_now`
    tcp_a=`expr $tcp_now - $tcp_last`
    #归一化处理（统计得）
    memory_a=`echo "$memory_a/100"|bc`
}
#重启apache服务器
restart_apache(){
   printf "\n***************************\n"
   printf "\n******* 攻 击 猛 烈 *******\n"
   printf "\n******* 重启apache服务器 *******\n"
   sudo service apache2 reload
   sudo a2ensite sitename.conf
   sudo service apache2 restart
   printf "\n******* 重 启 成 功 *******\n"
   printf "\n***************************\n"
}

increase(){
    touch /JIT_WAF/read/readfile.log  /JIT_WAF/read/predict.log
    a=`cat /JIT_WAF/read/readfile.log`
    skip=$a
    #从上一次读取的地方开始复制到新文件
    dd if=/var/log/apache2/access_blog.log of=/JIT_WAF/read/predict.log bs=1 skip=$skip
    #获取新增加内容的字节数  
    a1=`wc -c /JIT_WAF/read/predict.log | awk '{print $1}'`
    #获取总共需要skip 的字节数  
    sum=`expr $a + $a1`
    #记录到偏移量文件中，供下次读取  
    echo $sum>/JIT_WAF/read/readfile.log
     
}
#'/JIT_WAF/data_log/ip_out.log'
kill_ip(){
    #封禁ip
    cat /JIT_WAF/data_log/ip_out.log | while read line
    do
        ip=`echo $line | awk  -F ' ' '{print$1}'`
        type=`echo $line | awk  -F ' ' '{print$3}'`
        if [ $type -eq 1 ]; then
            printf "\n********* 封杀攻击IP **********\n"
            iptables -I INPUT -s $ip -j DROP
        fi
    done
}
send_mail(){
    echo "下方为攻击者地址" >> /JIT_WAF/e-mail/mail.txt 
    cat /JIT_WAF/data_log/ip_out.log | while read line
    do
        ip=`echo $line | awk  -F ' ' '{print$1}'` 
        type=`echo $line | awk  -F ' ' '{print$3}'`
        if [ $type -eq 1 ]; then
              echo $ip >> /JIT_WAF/e-mail/mail.txt   
        fi
    done
    mutt -s "告警" 1194370384@qq.com < /JIT_WAF/e-mail/mail.txt 
    rm /JIT_WAF/e-mail/mail.txt
}
#release_ip(){
    #释放ip
    #iptables -D INPUT -s ***.***.***.*** -j DROP
#}
    #启动程序
    printf "***************************\n"
    printf "**********JIT-WAF**********\n"
    printf "********** 启 动 **********\n"
    printf "***************************\n"
    printf "******* 实 时 监 测 *******\n"
    #开启时删除readfile
    rm /JIT_WAF/read/readfile.log

while :
do
    accelerated
    #定义触发条件
    #trigger=`echo "$memory_a+$tcp_a"|bc`
    #保证正常访问不产生predict.log临时文件
    printf "\n******* 保 驾 护 航 *******\n"
    increase
    if [ $memory_a -ge 30 -a $tcp_a -ge 10 ]; then
    echo "********** 发 生 攻 击 ***********"
    #向/var/log/apache2/access.log插入探针
    sleep 1s
    printf "\n"
    increase
    printf "\n"

    echo "********** 正 在 预 测 ***********"
    #数据预处理
    python /JIT_WAF/handle/handle.py
    #激活预测文件
    python /JIT_WAF/predict/predict.py
    #删除handle.py产生的文件
    rm /JIT_WAF/data_log/predict_data.log
    echo "********** 预 测 结 束 ***********"
    echo "********** 封 禁 攻 击 者 ***********"
    #查看文档'/JIT_WAF/data_log/ip_out.log'
    #封禁ip
    kill_ip
    echo "********** 发送告警邮件 **********"
    send_mail
    #清空'/JIT_WAF/data_log/ip_out.log'
    rm /JIT_WAF/data_log/ip_out.log
    #清空文档
    increase
    fi
    sleep 1s
done
