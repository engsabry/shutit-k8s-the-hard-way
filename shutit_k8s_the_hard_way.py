# Generated by shutit skeleton
import random
import datetime
import logging
import string
import os
import inspect
from shutit_module import ShutItModule

class shutit_k8s_the_hard_way(ShutItModule):


	def build(self, shutit):
		vagrant_image = shutit.cfg[self.module_id]['vagrant_image']
		vagrant_provider = shutit.cfg[self.module_id]['vagrant_provider']
		gui = shutit.cfg[self.module_id]['gui']
		memory = shutit.cfg[self.module_id]['memory']
		shutit.build['vagrant_run_dir'] = os.path.dirname(os.path.abspath(inspect.getsourcefile(lambda:0))) + '/vagrant_run'
		shutit.build['module_name'] = 'shutit_k8s_the_hard_way_' + ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))
		shutit.build['this_vagrant_run_dir'] = shutit.build['vagrant_run_dir'] + '/' + shutit.build['module_name']
		shutit.send(' command rm -rf ' + shutit.build['this_vagrant_run_dir'] + ' && command mkdir -p ' + shutit.build['this_vagrant_run_dir'] + ' && command cd ' + shutit.build['this_vagrant_run_dir'])
		shutit.send('command rm -rf ' + shutit.build['this_vagrant_run_dir'] + ' && command mkdir -p ' + shutit.build['this_vagrant_run_dir'] + ' && command cd ' + shutit.build['this_vagrant_run_dir'])
		if shutit.send_and_get_output('vagrant plugin list | grep landrush') == '':
			shutit.send('vagrant plugin install landrush')
		shutit.send('vagrant init ' + vagrant_image)
		shutit.send_file(shutit.build['this_vagrant_run_dir'] + '/Vagrantfile','''Vagrant.configure("2") do |config|
  config.landrush.enabled = true
  config.vm.provider "virtualbox" do |vb|
    vb.gui = ''' + gui + '''
    vb.memory = "''' + memory + '''"
  end

  config.vm.define "k8sc1" do |k8sc1|
    k8sc1.vm.box = ''' + '"' + vagrant_image + '"' + '''
    k8sc1.vm.hostname = "k8sc1.vagrant.test"
    config.vm.provider :virtualbox do |vb|
      vb.name = "shutit_k8s_the_hard_way_controller1"
    end
  end
  config.vm.define "k8sc2" do |k8sc2|
    k8sc2.vm.box = ''' + '"' + vagrant_image + '"' + '''
    k8sc2.vm.hostname = "k8sc2.vagrant.test"
    config.vm.provider :virtualbox do |vb|
      vb.name = "shutit_k8s_the_hard_way_controller2"
    end
  end
  config.vm.define "k8sc3" do |k8sc3|
    k8sc3.vm.box = ''' + '"' + vagrant_image + '"' + '''
    k8sc3.vm.hostname = "k8sc3.vagrant.test"
    config.vm.provider :virtualbox do |vb|
      vb.name = "shutit_k8s_the_hard_way_controller3"
    end
  end
  config.vm.define "k8sw1" do |k8sw1|
    k8sw1.vm.box = ''' + '"' + vagrant_image + '"' + '''
    k8sw1.vm.hostname = "k8sw1.vagrant.test"
    config.vm.provider :virtualbox do |vb|
      vb.name = "shutit_k8s_the_hard_way_worker1"
    end
  end
  config.vm.define "k8sw2" do |k8sw2|
    k8sw2.vm.box = ''' + '"' + vagrant_image + '"' + '''
    k8sw2.vm.hostname = "k8sw2.vagrant.test"
    config.vm.provider :virtualbox do |vb|
      vb.name = "shutit_k8s_the_hard_way_worker2"
    end
  end
  config.vm.define "k8sw3" do |k8sw3|
    k8sw3.vm.box = ''' + '"' + vagrant_image + '"' + '''
    k8sw3.vm.hostname = "k8sw3.vagrant.test"
    config.vm.provider :virtualbox do |vb|
      vb.name = "shutit_k8s_the_hard_way_worker3"
    end
  end
end''')

		# machines is a dict of dicts containing information about each machine for you to use.
		machines = {}
		machines.update({'k8sc1':{'fqdn':'k8sc1.vagrant.test'}})
		machines.update({'k8sc2':{'fqdn':'k8sc2.vagrant.test'}})
		machines.update({'k8sc3':{'fqdn':'k8sc3.vagrant.test'}})
		machines.update({'k8sw1':{'fqdn':'k8sw1.vagrant.test'}})
		machines.update({'k8sw2':{'fqdn':'k8sw2.vagrant.test'}})
		machines.update({'k8sw3':{'fqdn':'k8sw3.vagrant.test'}})

		try:
			pw = open('secret').read().strip()
		except IOError:
			pw = ''
		if pw == '':
			shutit.log("""You can get round this manual step by creating a 'secret' with your password: 'touch secret && chmod 700 secret'""",level=logging.CRITICAL)
			pw = shutit.get_env_pass()
			import time
			time.sleep(10)

		# Set up the sessions
		shutit_sessions = {}
		for machine in sorted(machines.keys()):
			shutit_sessions.update({machine:shutit.create_session('bash')})
		# Set up and validate landrush
		for machine in sorted(machines.keys()):
			shutit_session = shutit_sessions[machine]
			shutit_session.send('cd ' + shutit.build['this_vagrant_run_dir'])
			# Remove any existing landrush entry.
			shutit_session.send('vagrant landrush rm ' + machines[machine]['fqdn'])
			# Needs to be done serially for stability reasons.
			try:
				shutit_session.multisend('vagrant up --provider ' + shutit.cfg['shutit-library.virtualization.virtualization.virtualization']['virt_method'] + machine_name,{'assword for':pw,'assword:':pw})
			except NameError:
				shutit.multisend('vagrant up ' + machine,{'assword for':pw,'assword:':pw},timeout=99999)
			if shutit.send_and_get_output("vagrant status 2> /dev/null | grep -w ^" + machine + " | awk '{print $2}'") != 'running':
				shutit.pause_point("machine: " + machine + " appears not to have come up cleanly")
			ip = shutit.send_and_get_output('''vagrant landrush ls 2> /dev/null | grep -w ^''' + machines[machine]['fqdn'] + ''' | awk '{print $2}' ''')
			machines.get(machine).update({'ip':ip})
			shutit_session.login(command='vagrant ssh ' + machine)
			shutit_session.login(command='sudo su - ')
			shutit_session.send('sysctl -w net.ipv4.conf.all.route_localnet=1')
			# Correct /etc/hosts
			shutit_session.send(r'''cat <(echo $(ip -4 -o addr show scope global | grep -v 10.0.2.15 | head -1 | awk '{print $4}' | sed 's/\(.*\)\/.*/\1/') $(hostname)) <(cat /etc/hosts | grep -v $(hostname -s)) > /tmp/hosts && mv -f /tmp/hosts /etc/hosts''')
			# Correct any broken ip addresses.
			if shutit.send_and_get_output('''vagrant landrush ls | grep ''' + machine + ''' | grep 10.0.2.15 | wc -l''') != '0':
				shutit_session.log('A 10.0.2.15 landrush ip was detected for machine: ' + machine + ', correcting.',level=logging.WARNING)
				# This beaut gets all the eth0 addresses from the machine and picks the first one that it not 10.0.2.15.
				while True:
					ipaddr = shutit_session.send_and_get_output(r'''ip -4 -o addr show scope global | grep -v 10.0.2.15 | head -1 | awk '{print $4}' | sed 's/\(.*\)\/.*/\1/' ''')
					if ipaddr[0] not in ('1','2','3','4','5','6','7','8','9'):
						time.sleep(10)
					else:
						break
				# Send this on the host (shutit, not shutit_session)
				shutit.send('vagrant landrush set ' + machines[machine]['fqdn'] + ' ' + ipaddr)
			# Check that the landrush entry is there.
			shutit.send('vagrant landrush ls | grep -w ' + machines[machine]['fqdn'])
		# Gather landrush info
		for machine in sorted(machines.keys()):
			ip = shutit.send_and_get_output('''vagrant landrush ls 2> /dev/null | grep -w ^''' + machines[machine]['fqdn'] + ''' | awk '{print $2}' ''')
			machines.get(machine).update({'ip':ip})


		###############################################################################
		# Set root password
		root_pass = 'lowbunker'
		###############################################################################

		###############################################################################
		# Set up hosts for chef appropriate for their role
		for machine in sorted(machines.keys()):
			shutit_session = shutit_sessions[machine]
			# Set root password
			shutit_session.send('echo root:' + root_pass + ' | /usr/sbin/chpasswd')
			shutit_session.send('cd /root')

		for machine in sorted(machines.keys()):
			shutit_session = shutit_sessions[machine]
			for to_machine in sorted(machines.keys()):
				shutit_session.multisend('ssh-copy-id root@' + to_machine + '.vagrant.test',{'ontinue connecting':'yes','assword':root_pass})
				shutit_session.multisend('ssh-copy-id root@' + to_machine,{'ontinue connecting':'yes','assword':root_pass})

		for machine in sorted(machines.keys()):
			shutit_session = shutit_sessions[machine]
			shutit_session.run_script(r'''#!/bin/sh
# See https://raw.githubusercontent.com/ianmiell/vagrant-swapfile/master/vagrant-swapfile.sh
fallocate -l ''' + shutit.cfg[self.module_id]['swapsize'] + r''' /swapfile
ls -lh /swapfile
chown root:root /swapfile
chmod 0600 /swapfile
ls -lh /swapfile
mkswap /swapfile
swapon /swapfile
swapon -s
grep -i --color swap /proc/meminfo
echo "
/swapfile none            swap    sw              0       0" >> /etc/fstab''')
			shutit_session.multisend('adduser person',{'Enter new UNIX password':'person','Retype new UNIX password:':'person','Full Name':'','Phone':'','Room':'','Other':'','Is the information correct':'Y'})

		# https://github.com/kelseyhightower/kubernetes-the-hard-way/blob/master/docs/02-client-tools.md
		for machine in sorted(machines.keys()):
			shutit_session = shutit_sessions[machine]
			shutit_session.send('wget -q --show-progress --https-only --timestamping https://pkg.cfssl.org/R1.2/cfssl_linux-amd64 https://pkg.cfssl.org/R1.2/cfssljson_linux-amd64')
			shutit_session.send('chmod +x cfssl_linux-amd64 cfssljson_linux-amd64')
			shutit_session.send('mv cfssl_linux-amd64 /usr/local/bin/cfssl')
			shutit_session.send('mv cfssljson_linux-amd64 /usr/local/bin/cfssljson')
			shutit_session.send('wget https://storage.googleapis.com/kubernetes-release/release/v1.10.2/bin/linux/amd64/kubectl')
			shutit_session.send('chmod +x kubectl')
			shutit_session.send('mv kubectl /usr/local/bin/')

		# https://github.com/kelseyhightower/kubernetes-the-hard-way/blob/master/docs/04-certificate-authority.md
		# Certificate Authority

		shutit_session_k8sc1 = shutit_sessions['k8sc1']
		shutit_session_k8sc1.send('''cat > ca-config.json <<EOF
{
  "signing": {
    "default": {
      "expiry": "8760h"
    },
    "profiles": {
      "kubernetes": {
        "usages": ["signing", "key encipherment", "server auth", "client auth"],
        "expiry": "8760h"
      }
    }
  }
}
EOF''')
		shutit_session_k8sc1.send('''cat > ca-csr.json <<EOF
{
  "CN": "Kubernetes",
  "key": {
    "algo": "rsa",
    "size": 2048
  },
  "names": [
    {
      "C": "US",
      "L": "Portland",
      "O": "Kubernetes",
      "OU": "CA",
      "ST": "Oregon"
    }
  ]
}
EOF''')
		shutit_session_k8sc1.send('cfssl gencert -initca ca-csr.json | cfssljson -bare ca')

		# Admin client certs
		shutit_session_k8sc1.send('''cat > admin-csr.json <<EOF
{
  "CN": "admin",
  "key": {
    "algo": "rsa",
    "size": 2048
  },
  "names": [
    {
      "C": "US",
      "L": "Portland",
      "O": "system:masters",
      "OU": "Kubernetes The Hard Way",
      "ST": "Oregon"
    }
  ]
}
EOF''')
		shutit_session_k8sc1.send('cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=kubernetes admin-csr.json | cfssljson -bare admin')

		# Kubelet client certs
		for machine in sorted(machines.keys()):
			shutit_session = shutit_sessions[machine]
			if machine in ('k8sw1','k8sw2','k8sw3'):
				shutit_session_k8sc1.send('''cat > ''' + machine + '''-csr.json <<EOF
{
  "CN": "system:node:''' + machine + '''",
  "key": {
    "algo": "rsa",
    "size": 2048
  },
  "names": [
    {
      "C": "US",
      "L": "Portland",
      "O": "system:nodes",
      "OU": "Kubernetes The Hard Way",
      "ST": "Oregon"
    }
  ]
}
EOF''')
				shutit_session_k8sc1.send('EXTERNAL_IP=' + machines[machine]['ip'])
				shutit_session_k8sc1.send('INTERNAL_IP=' + machines[machine]['ip'])
				shutit_session_k8sc1.send('''cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -hostname=''' + machine + ''',${EXTERNAL_IP},${INTERNAL_IP} -profile=kubernetes ''' + machine + '''-csr.json | cfssljson -bare ''' + machine)


		# Controller manager client certs
		shutit_session_k8sc1.send('''cat > kube-controller-manager-csr.json <<EOF
{
  "CN": "system:kube-controller-manager",
  "key": {
    "algo": "rsa",
    "size": 2048
  },
  "names": [
    {
      "C": "US",
      "L": "Portland",
      "O": "system:kube-controller-manager",
      "OU": "Kubernetes The Hard Way",
      "ST": "Oregon"
    }
  ]
}
EOF''')
		shutit_session_k8sc1.send('''cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=kubernetes kube-controller-manager-csr.json | cfssljson -bare kube-controller-manager''')


		# Kube proxy client certificate
		shutit_session_k8sc1.send('''cat > kube-proxy-csr.json <<EOF
{
  "CN": "system:kube-proxy",
  "key": {
    "algo": "rsa",
    "size": 2048
  },
  "names": [
    {
      "C": "US",
      "L": "Portland",
      "O": "system:node-proxier",
      "OU": "Kubernetes The Hard Way",
      "ST": "Oregon"
    }
  ]
}
EOF''')
		shutit_session_k8sc1.send('''cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=kubernetes kube-proxy-csr.json | cfssljson -bare kube-proxy''')

		# Scheduler client certificate
		shutit_session_k8sc1.send('''cat > kube-scheduler-csr.json <<EOF
{
  "CN": "system:kube-scheduler",
  "key": {
    "algo": "rsa",
    "size": 2048
  },
  "names": [
    {
      "C": "US",
      "L": "Portland",
      "O": "system:kube-scheduler",
      "OU": "Kubernetes The Hard Way",
      "ST": "Oregon"
    }
  ]
}
EOF''')
		shutit_session_k8sc1.send('''cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=kubernetes kube-scheduler-csr.json | cfssljson -bare kube-scheduler''')

		# Kubernetes API server cert
		shutit_session_k8sc1.send('EXTERNAL_IP=' + machines['k8sc1']['ip'])
		shutit_session_k8sc1.send('''cat > kubernetes-csr.json <<EOF
{
  "CN": "kubernetes",
  "key": {
    "algo": "rsa",
    "size": 2048
  },
  "names": [
    {
      "C": "US",
      "L": "Portland",
      "O": "Kubernetes",
      "OU": "Kubernetes The Hard Way",
      "ST": "Oregon"
    }
  ]
}
EOF''')
		shutit_session_k8sc1.send('''cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -hostname=10.32.0.1,10.240.0.10,10.240.0.11,10.240.0.12,${KUBERNETES_PUBLIC_ADDRESS},127.0.0.1,kubernetes.default -profile=kubernetes kubernetes-csr.json | cfssljson -bare kubernetes''')

		# Service account key pair
		shutit_session_k8sc1.send('''cat > service-account-csr.json <<EOF
{
  "CN": "service-accounts",
  "key": {
    "algo": "rsa",
    "size": 2048
  },
  "names": [
    {
      "C": "US",
      "L": "Portland",
      "O": "Kubernetes",
      "OU": "Kubernetes The Hard Way",
      "ST": "Oregon"
    }
  ]
}
EOF''')
		shutit_session_k8sc1.send('cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=kubernetes service-account-csr.json | cfssljson -bare service-account')


		for machine in sorted(machines.keys()):
			shutit_session = shutit_sessions[machine]
			if machine in ('k8sw1','k8sw2','k8sw3'):
				shutit_session_k8sc1.send('scp ca.pem ' + machine + '-key.pem ' + machine + '.pem ' + machine + ':~/')
			if machine in ('k8sc1','k8sc2','k8sc3'):
  				shutit_session_k8sc1.send('scp ca.pem ca-key.pem kubernetes-key.pem kubernetes.pem service-account-key.pem service-account.pem ' + machine + ':~/')

		# https://github.com/kelseyhightower/kubernetes-the-hard-way/blob/master/docs/05-kubernetes-configuration-files.md
		shutit_session_k8sc1.send('KUBERNETES_PUBLIC_ADDRESS=' + machines['k8sc1']['ip'])


		for machine in sorted(machines.keys()):
			shutit_session = shutit_sessions[machine]
			if machine in ('k8sw1','k8sw2','k8sw3'):
				shutit_session.send('kubectl config set-cluster kubernetes-the-hard-way --certificate-authority=ca.pem --embed-certs=true --server=https://${KUBERNETES_PUBLIC_ADDRESS}:6443 --kubeconfig=' + machine + '.kubeconfig')
				shutit_session.send('kubectl config set-credentials system:node:' + machine + ' --client-certificate=' + machine + '.pem --client-key=${instance}-key.pem --embed-certs=true --kubeconfig=' + machine + '.kubeconfig')
				shutit_session.send('kubectl config set-context default --cluster=kubernetes-the-hard-way --user=system:node:' + machine + ' --kubeconfig=' + machine + '.kubeconfig')
				shutit_session.send('kubectl config use-context default --kubeconfig=' + machine + '.kubeconfig')

		shutit_session_k8sc1.send('kubectl config set-cluster kubernetes-the-hard-way --certificate-authority=ca.pem --embed-certs=true --server=https://${KUBERNETES_PUBLIC_ADDRESS}:6443 --kubeconfig=kube-proxy.kubeconfig')
		shutit_session_k8sc1.send('kubectl config set-credentials system:kube-proxy --client-certificate=kube-proxy.pem --client-key=kube-proxy-key.pem --embed-certs=true --kubeconfig=kube-proxy.kubeconfig')
		shutit_session_k8sc1.send('kubectl config set-context default --cluster=kubernetes-the-hard-way --user=system:kube-proxy --kubeconfig=kube-proxy.kubeconfig')
		shutit_session_k8sc1.send('kubectl config use-context default --kubeconfig=kube-proxy.kubeconfig')

		shutit_session_k8sc1.send('kubectl config set-cluster kubernetes-the-hard-way --certificate-authority=ca.pem --embed-certs=true --server=https://127.0.0.1:6443 --kubeconfig=kube-controller-manager.kubeconfig')
		shutit_session_k8sc1.send('kubectl config set-credentials system:kube-controller-manager --client-certificate=kube-controller-manager.pem --client-key=kube-controller-manager-key.pem --embed-certs=true --kubeconfig=kube-controller-manager.kubeconfig')
		shutit_session_k8sc1.send('kubectl config set-context default --cluster=kubernetes-the-hard-way --user=system:kube-controller-manager --kubeconfig=kube-controller-manager.kubeconfig')
		shutit_session_k8sc1.send('kubectl config use-context default --kubeconfig=kube-controller-manager.kubeconfig')

		shutit_session_k8sc1.send('kubectl config set-cluster kubernetes-the-hard-way --certificate-authority=ca.pem --embed-certs=true --server=https://127.0.0.1:6443 --kubeconfig=kube-scheduler.kubeconfig')
		shutit_session_k8sc1.send('kubectl config set-credentials system:kube-scheduler --client-certificate=kube-scheduler.pem --client-key=kube-scheduler-key.pem --embed-certs=true --kubeconfig=kube-scheduler.kubeconfig')
		shutit_session_k8sc1.send('kubectl config set-context default --cluster=kubernetes-the-hard-way --user=system:kube-scheduler --kubeconfig=kube-scheduler.kubeconfig')
		shutit_session_k8sc1.send('kubectl config use-context default --kubeconfig=kube-scheduler.kubeconfig')

		shutit_session_k8sc1.send('kubectl config set-cluster kubernetes-the-hard-way --certificate-authority=ca.pem --embed-certs=true --server=https://127.0.0.1:6443 --kubeconfig=admin.kubeconfig')
		shutit_session_k8sc1.send('kubectl config set-credentials admin --client-certificate=admin.pem --client-key=admin-key.pem --embed-certs=true --kubeconfig=admin.kubeconfig')
		shutit_session_k8sc1.send('kubectl config set-context default --cluster=kubernetes-the-hard-way --user=admin --kubeconfig=admin.kubeconfig')
		shutit_session_k8sc1.send('kubectl config use-context default --kubeconfig=admin.kubeconfig')

		for machine in sorted(machines.keys()):
			shutit_session = shutit_sessions[machine]
			if machine in ('k8sw1','k8sw2','k8sw3'):
				shutit_session_k8sc1.send('scp ' + machine + '.kubeconfig kube-proxy.kubeconfig ' + machine + ':~/')
			if machine in ('k8sc1','k8sc2','k8sc3'):
				shutit_session_k8sc1.send('scp admin.kubeconfig kube-controller-manager.kubeconfig kube-scheduler.kubeconfig ' + machine + ':~/')

		# https://github.com/ianmiell/kubernetes-the-hard-way/blob/master/docs/06-data-encryption-keys.md
		shutit_session_k8sc1.send('ENCRYPTION_KEY=$(head -c 32 /dev/urandom | base64)')
		shutit_session_k8sc1.send('''cat > encryption-config.yaml <<EOF
kind: EncryptionConfig
apiVersion: v1
resources:
  - resources:
      - secrets
    providers:
      - aescbc:
          keys:
            - name: key1
              secret: ${ENCRYPTION_KEY}
      - identity: {}
EOF''')
		for machine in sorted(machines.keys()):
			shutit_session = shutit_sessions[machine]
			if machine in ('k8sc1','k8sc2','k8sc3'):
				shutit_session_k8sc1.send('scp encryption-config.yaml ' + machine + ':~/')

		# https://github.com/ianmiell/kubernetes-the-hard-way/blob/master/docs/07-bootstrapping-etcd.md
		for machine in sorted(machines.keys()):
			shutit_session = shutit_sessions[machine]
			if machine in ('k8sc1','k8sc2','k8sc3'):
				shutit_session.send('wget -q --show-progress --https-only --timestamping "https://github.com/coreos/etcd/releases/download/v3.3.5/etcd-v3.3.5-linux-amd64.tar.gz"')
				shutit_session.send('tar -xvf etcd-v3.3.5-linux-amd64.tar.gz')
				shutit_session.send('mv etcd-v3.3.5-linux-amd64/etcd* /usr/local/bin/')
				shutit_session.send('mkdir -p /etc/etcd /var/lib/etcd')
				shutit_session.send('cp ca.pem kubernetes-key.pem kubernetes.pem /etc/etcd/')
				shutit_session.send('INTERNAL_IP=' + machines[machine]['ip'])
				shutit_session.send('ETCD_NAME=$(hostname -s)')
				shutit_session.send('''cat <<EOF | sudo tee /etc/systemd/system/etcd.service
[Unit]
Description=etcd
Documentation=https://github.com/coreos

[Service]
ExecStart=/usr/local/bin/etcd --name ${ETCD_NAME} --cert-file=/etc/etcd/kubernetes.pem --key-file=/etc/etcd/kubernetes-key.pem --peer-cert-file=/etc/etcd/kubernetes.pem --peer-key-file=/etc/etcd/kubernetes-key.pem --trusted-ca-file=/etc/etcd/ca.pem --peer-trusted-ca-file=/etc/etcd/ca.pem --peer-client-cert-auth --client-cert-auth --initial-advertise-peer-urls https://${INTERNAL_IP}:2380 --listen-peer-urls https://${INTERNAL_IP}:2380 --listen-client-urls https://${INTERNAL_IP}:2379,https://127.0.0.1:2379 --advertise-client-urls https://${INTERNAL_IP}:2379 --initial-cluster-token etcd-cluster-0 --initial-cluster k8sc1=https://10.240.0.10:2380,k8sc2=https://10.240.0.11:2380,k8sc3=https://10.240.0.12:2380 --initial-cluster-state new --data-dir=/var/lib/etcd
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF''')
				shutit_session.send('systemctl daemon-reload')
				shutit_session.send('systemctl enable etcd')

		for machine in sorted(machines.keys()):
			shutit_session = shutit_sessions[machine]
			if machine in ('k8sc1','k8sc2','k8sc3'):
				shutit_session.send('systemctl start etcd')

		shutit_session_k8sc1.send_until('ETCDCTL_API=3 etcdctl member list --endpoints=https://127.0.0.1:2379 --cacert=/etc/etcd/ca.pem --cert=/etc/etcd/kubernetes.pem --key=/etc/etcd/kubernetes-key.pem | grep -w started | wc -l','3')

		for machine in sorted(machines.keys()):
			shutit_session = shutit_sessions[machine]
			shutit_session.send('hostname')
			shutit_session.pause_point('ok')


		return True


	def get_config(self, shutit):
		shutit.get_config(self.module_id,'vagrant_image',default='ubuntu/bionic64')
		shutit.get_config(self.module_id,'vagrant_provider',default='virtualbox')
		shutit.get_config(self.module_id,'gui',default='false')
		shutit.get_config(self.module_id,'memory',default='1024')
		shutit.get_config(self.module_id,'swapsize',default='2G')
		return True

	def test(self, shutit):
		return True

	def finalize(self, shutit):
		return True

	def is_installed(self, shutit):
		return False

	def start(self, shutit):
		return True

	def stop(self, shutit):
		return True

def module():
	return shutit_k8s_the_hard_way(
		'git.shutit_k8s_the_hard_way.shutit_k8s_the_hard_way', 1403397676.0001,
		description='',
		maintainer='',
		delivery_methods=['bash'],
		depends=['shutit.tk.setup','shutit-library.virtualization.virtualization.virtualization','tk.shutit.vagrant.vagrant.vagrant']
	)
