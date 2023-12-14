#!/usr/bin/bash

# Create user  debian-based image

UserName=$1
UserId=$2
GroupName=$3
GroupId=$4
Shell=$5

echo "Create user:"
echo " - user.id     ${UserId}"
echo " - user.name   ${UserName}"
echo " - group.id    ${GroupId}"
echo " - group.name  ${GroupName}"
echo " - shell       ${Shell}"
echo " - sudo        password-free"

mkdir -p /etc/sudoers.d
echo "$UserName ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/nopasswd

groupadd -g "$GroupId" "$GroupName"
useradd -m -u "$UserId" -d "/home/$UserName" -g "$GroupId" -s $Shell "$UserName"

sudo chown $UserName:$GroupName /home/$UserName