#!/usr/bin/env bash
set -euxo pipefail

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y nfs-kernel-server

DEVICE_PATH="/dev/disk/by-id/google-${disk_name}"

if ! blkid "$DEVICE_PATH"; then
  mkfs.ext4 -m 0 -E lazy_itable_init=0,lazy_journal_init=0,discard "$DEVICE_PATH"
fi

mkdir -p "${nfs_dir}"
DISK_UUID=$(blkid -s UUID -o value "$DEVICE_PATH")

if ! grep -q "$DISK_UUID" /etc/fstab; then
  echo "UUID=$DISK_UUID ${nfs_dir} ext4 discard,defaults,nofail 0 2" >> /etc/fstab
fi

mount -a
chown nobody:nogroup "${nfs_dir}"
chmod 0777 "${nfs_dir}"

cat <<EOF > /etc/exports
${nfs_dir} ${cidr}(rw,sync,no_subtree_check,no_root_squash) 10.0.0.0/8(rw,sync,no_subtree_check,no_root_squash)
EOF

exportfs -ra
systemctl enable nfs-kernel-server
systemctl restart nfs-kernel-server
