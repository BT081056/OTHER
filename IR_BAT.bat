@echo off
chcp 65001

set "hostname=raspberry pi"  REM 将主机名替换为你要查询的实际主机名

REM 使用 ping 命令获取主机名的 IP 地址
for /f "tokens=2 delims=[]" %%i in ('ping -4 -n 1 %hostname% ^| findstr /i "Pinging"') do set "ip=%%i"

REM 输出 IP 地址
echo %hostname% 的 IP 地址是：%ip%


set "url=http://192.168.105.201/thermal_data"

REM 使用 curl 命令获取网页内容并重定向到临时文件
curl "%url%" > temp.html

REM 检查 curl 命令是否执行成功
if %ERRORLEVEL% equ 0 (
    REM 使用 findstr 命令查找包含数字的行并保存到临时文件
    findstr /R /C:"[0-9]*\.[0-9]*,[0-9]*\.[0-9]*" temp.html > temp_result.txt

    REM 使用 for /f 命令读取临时文件的内容并找到最大值并保存到临时变量
    setlocal enabledelayedexpansion
    set "max_value=0"
    for /f "usebackq tokens=1 delims=," %%i in ("temp_result.txt") do (
        set "value=%%i"
        REM 删除值中的所有空格（可选步骤）
        set "value=!value: =!"
        REM 将值转换为浮点数（保留小数点）
        set "value=!value:.,=!"
        set /a "int_value=value"
        set "decimal_part=!value:~-2!"
        set "float_value=!int_value!.!decimal_part!"
        REM 判断是否为最大值
        if !float_value! gtr !max_value! set "max_value=!float_value!"
    )

    REM 将最大值保存到临时文件
    echo 最大值是：!max_value! > temp_result_max.txt
	set "api_url=http://example.com/api/endpoint"  REM 替换为实际的 API URL
	set "data={\"key1\":\"value1\",\"key2\":\"value2\"}"  REM 替换为要发送的 JSON 数据

	REM 使用 curl 命令发送 POST 请求
	curl -X POST -H "Content-Type: application/json" -d "%data%" "%api_url"

    REM 使用 type 命令读取临时文件内容并打印出来
    type temp_result_max.txt

    REM 删除临时文件
    del temp_result.txt
    del temp_result_max.txt
	
	
	
) else (
    echo 请求失败，状态码：%ERRORLEVEL%
)

REM 删除临时文件
del temp.html

