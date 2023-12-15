Distro=$1
UserName=$2
UserId=$3
GroupName=$4
GroupId=$5
Shell=$6

echo "Create user:"
echo " - distro      ${Distro}"
echo " - user.id     ${UserId}"
echo " - user.name   ${UserName}"
echo " - group.id    ${GroupId}"
echo " - group.name  ${GroupName}"
echo " - shell       ${Shell}"
echo " - sudo        password-free"

debian() {
  useradd -m -u "$UserId" -d "/home/$UserName" -g "$GroupId" -s "$Shell" "$UserName"
}

alpine() {
  adduser -u "$UserId" -G "$GroupName" -s "$Shell" -D -h "/home/$UserName" "$UserName"
}

mkdir -p /etc/sudoers.d
echo "$UserName ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/nopasswd
groupadd -g "$GroupId" "$GroupName"
sudo chown "$UserName:$GroupName" "/home/$UserName"

$Distro
