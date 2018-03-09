#! /bin/sh
# create by Arrui.c@gmail.com 
# Version code:2.0
# 命令使用方法 btc.sh [美元汇率（默认6.3）] [10000算力btc每天收益] [当前一个btc价格] [1算力成本（默认838）] [电费成本（单位kw/h，默认0.35）] 
if [ $# -lt 3 ] ; then
echo "命令使用方法 btc.sh [美元汇率（默认6.3）] [10000算力btc每天收益] [当前一个btc价格] [1算力成本（默认838）] [电费成本（单位kw/h，默认0.35）]"
exit 0
fi
# 参数1 =======>> 美元汇率（默认6.3）
# 参数2 =======>> 10000算力btc每天收益（单位个）
# 参数3 =======>> 当前一个btc价格
# 参数4 =======>> 1算力成本
# 参数5 =======>> 电费成本（单位kw/h，默认0.35）
# 美元汇率（默认6.3）
USD_rate=$1
# 1算力成本
# 电费成本（单位kw/h）
if [ $# -eq 3 ];then
	one_calculate_fee=838
	electricity_unit_price=0.35
elif [ $# -eq 4 ];then
	one_calculate_fee=$4
	electricity_unit_price=0.35
elif [ $# -eq 5 ];then
	one_calculate_fee=$4
	electricity_unit_price=$5
fi
echo "美元汇率" $1
echo "10000算力btc每天收益（单位个）:" $2
echo "当前一个btc价格:" $3"RMB"
echo "1算力成本:" $one_calculate_fee
echo "电费成本（单位kw/h，默认0.35）:" $electricity_unit_price

# 总算力成本
total_calculate_fee=$(($one_calculate_fee*10000))
# 设备1年折旧率80%
machine_depreciation_rate=0.8
# echo $total_calculate_fee
# 总维护费用(冷却通风、厂房折旧或租赁、变压器改造等，属于一次性投入，可维持3年算)
total_maintance_fee=680000
# 每天设备折旧费用，维护费用
# echo $(($total_maintance_fee/(365*3)))
one_day_fee=$(($(echo "$total_calculate_fee*$machine_depreciation_rate/365"|bc)+$(($total_maintance_fee/(365*3)))))
# echo $one_day_fee
# 每天电力费用
electricity_fee=$(echo "$electricity_unit_price*24*10"|bc)
# echo $electricity_fee
# 每天人力成本，按时薪100算，一天2400
human_resorce_fee=2400
#融资率0.8
financing_rate=0.8
# financing_rate=0
# 前期一次性投入费用
pre_investment_fee=$(echo "$(($total_calculate_fee+$total_maintance_fee))*$(echo "1-$financing_rate"|bc)"|bc)
# echo $pre_investment_fee
# 每天融资费用，融资率80%，融资成本15%每年，按贷款30年算
financing_fee=$(echo "$(($total_calculate_fee+$total_maintance_fee))*$financing_rate"|bc)
# echo $financing_fee
financing_fee_one_day=4215
# financing_fee_one_day=0
# echo $financing_fee_one_day

# 每天总费用
total_fee_one_day=$(echo "$one_day_fee+$electricity_fee+$financing_fee_one_day+$human_resorce_fee"|bc)
echo "每日总费用" $total_fee_one_day "RMB" "≈" $(echo "$total_fee_one_day/$USD_rate"|bc)"USD"

if [ ! -n '$2' ];then
	echo "请输入每日btc收益（10000算力）"
else
	if [ ! -n '$3' ];then
		echo "请输入当前btc价格"
	else
	btc_l_price=$(echo "$total_fee_one_day / $2" |bc)
	echo "btc保底价格:" $btc_l_price "RMB" "≈" $(echo "$btc_l_price/$USD_rate"|bc)"USD"
	echo "btc实时价格:" $3 "RMB" "≈" $(echo "$3/$USD_rate"|bc)"USD"
	echo "btc当前溢价:" $(echo "$(echo "scale=2; $3 / $btc_l_price"|bc)*100"|bc) "%"
	
	profit_one_day=$(echo "$(echo "$3 * $2"|bc) - $total_fee_one_day"|bc)
	echo "当天净利润:" $profit_one_day "RMB" "≈" $(echo "$profit_one_day/$USD_rate"|bc)"USD"
	recover_days=$(echo "$(($total_calculate_fee+$total_maintance_fee))/$profit_one_day"|bc)
	echo "回本天数:" $recover_days "天"
	echo "资金回笼/动态平衡:" $(echo "$pre_investment_fee/$profit_one_day"|bc) "天"
	echo "年化收益率:" $(echo "$(echo "scale=2;$profit_one_day/$total_fee_one_day"|bc)*100"|bc) "%"
 	echo "年净利润:" $(echo "$profit_one_day*365/10000"|bc)"万RMB"
	fi
fi
