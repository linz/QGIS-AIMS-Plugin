################################################################################
#
# Copyright 2013 Crown copyright (c)
# Land Information New Zealand and the New Zealand Government.
# All rights reserved
#
# This program is released under the terms of the new BSD license. See the
# LICENSE file for more information.
#
################################################################################

#
### CONFIGURATION SECTION
#

Vagrant.require_version ">= 1.7.0"

BOX = "trusty-canonical"
BOX_URL = "http://cloud-images.ubuntu.com/vagrant/trusty/current/trusty-server-cloudimg-i386-vagrant-disk1.box"

SERVERS = {
    # database
    "db" => {
        "memory" => "512",
        "ports" => [
            ["5432", "15432"],
       ]
    },
    # load balancer
    "lb" => {
       "memory" => "512",
        "ports" => [
            ["8100", "18100"],
            ["80", "10080"],
       ]
    },
    # web service 1
    "web_1" => {
        "memory" => "512",
        "ports" => [
            ["8000", "18000"],
       ]
    },
    # web service 2
    "web_2" => {
        "memory" => "512",
        "ports" => [
            ["8000", "18000"],
       ]
    }
}


#
### DON'T CHANGE ANYTHING UNDER THIS LINE
#

Vagrant.configure(2) do |config|

    config.vm.box = BOX
    config.vm.box_url = BOX_URL

    config.ssh.forward_agent = true
    config.vm.synced_folder '.', '/vagrant'


    # loop over all configured servers
    SERVERS.each do | (name, cfg) |
        config.vm.define name do |server|

            # IP address
            server.vm.network "private_network",
                type: "dhcp"

            # hostname
            server.vm.hostname = name.gsub("_", "-")

            # ports forwarding
            cfg["ports"].each do | port |
                server.vm.network "forwarded_port",
                    guest: port[0],
                    host: port[1],
                    auto_correct: true
            end

            ### DEPLOYMENT
            sname = name.gsub(/_.*/, "")  # server name without number
            server.vm.provision "deploy", type: "ansible" do |ansible|
                ansible.playbook = "provision/" + sname + "-deploy.yml"
                ansible.limit = "all"
                ansible.groups = {
                    "web" => ["web_1", "web_2"],
                }
                ansible.verbose = "vv"

                # load password from file if exists
                if File.exist?('ansible-password.txt')
                    ansible.vault_password_file = "ansible-password.txt"
                else
                    ansible.ask_vault_pass = true
                end
            end

            ### TEST
            server.vm.provision "test", type: "ansible" do |ansible|
                ansible.playbook = "provision/" + sname + "-test.yml"
                ansible.limit = "all"
                ansible.groups = {
                    "web" => ["web_1", "web_2"],
                }
                ansible.verbose = "vv"
            end

            ### PROVIDERS CONFIGURATION
            # VirtualBox
            server.vm.provider "virtualbox" do |vb, override|
                vb.customize ["modifyvm", :id, "--memory", cfg["memory"]]
                vb.customize ["modifyvm", :id, "--nictype1", "virtio"]
                vb.customize ["modifyvm", :id, "--nictype2", "virtio"]
#               vb.gui = true
            end
        end
    end
end

