import paramiko

client = paramiko.SSHClient()

host = ''
username = ''
password = ''

try:
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # avoid exception: Server not found in knows host
    client.connect(host, username=username, password=password)
    print("[+] Getting list of application...\n")
    stdin, stdout, stderr = client.exec_command('find /var/containers/Bundle/Application/ -name "*.app"')

    if stderr != '':
        for line in stdout.readlines():
            print(line.strip())
    else:
        print(stderr.read())
        raise Exception("Can not get list of installed app!")
    target_app = input("\n[+] Enter an application path above: ")

    if not target_app.startswith("/var/containers/Bundle/Application/") or not target_app.endswith(".app"):
        raise Exception("Application path is incorrect")

    app_name = target_app.split("/")[-1].replace(" ", "").replace(".app", "")
    print("[+] Pulling " + app_name + ".ipa ...")
    client.exec_command('rm -rf /tmp/Payload')
    client.exec_command('rm ' + app_name + '.ipa')
    client.exec_command('mkdir /tmp/Payload')

    stdin, stdout, stderr = client.exec_command('cp -r "' + target_app + '" ' + '/tmp/Payload')
    exit_status = stdout.channel.recv_exit_status()  # make sure the cp command run successfully
    if exit_status == 0:
        stdin, stdout, stderr = client.exec_command('cd /tmp && ' + 'zip -r ' + app_name + '.ipa ' + 'Payload')
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            ftp_client = client.open_sftp()
            ftp_client.get('/tmp/' + app_name + '.ipa', app_name + '.ipa')
            ftp_client.close()
            print("[+] Done")
        else:
            stderr.read()
    else:
        print(stderr.read())
except Exception as e:
    print("Exception: " + str(e))
finally:
    client.close()
    del client, stdin, stdout, stderr  # avoid exception: Exception ignored in...
