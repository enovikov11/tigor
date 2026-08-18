<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:cfg="urn:vm-config"
  xmlns:exsl="http://exslt.org/common"
  extension-element-prefixes="exsl"
  exclude-result-prefixes="cfg exsl">
  <xsl:output method="xml" encoding="UTF-8" indent="yes"/>

  <xsl:template match="/">
    <xsl:for-each select="/xsl:stylesheet/cfg:vm">
      <exsl:document href="{concat(@name, '.xml')}" method="xml" encoding="UTF-8" indent="yes">
        <xsl:apply-templates select="."/>
      </exsl:document>
    </xsl:for-each>
  </xsl:template>

  <xsl:template match="cfg:vm">
    <domain type="kvm">
      <name><xsl:value-of select="@name"/></name>
      <memory unit="GiB"><xsl:value-of select="@ram"/></memory>
      <memoryBacking>
        <xsl:choose>
            <xsl:when test="@hardened = 'true'"><locked/></xsl:when>
            <xsl:when test="cfg:mount"><source type="memfd"/><access mode="shared"/></xsl:when>
        </xsl:choose>
      </memoryBacking>
      <vcpu><xsl:value-of select="@cpu"/></vcpu>
      <os>
        <type arch="x86_64" machine="pc-q35-10.2">hvm</type>
        <loader readonly="yes" type="pflash" stateless="yes" format="raw">/run/libvirt/nix-ovmf/edk2-x86_64-code.fd</loader>
        <xsl:choose>
          <xsl:when test="@kernel"><kernel><xsl:value-of select="@kernel"/></kernel></xsl:when>
          <xsl:otherwise><boot dev="hd"/></xsl:otherwise>
        </xsl:choose>
      </os>
      <features><acpi/><apic/><ioapic driver="kvm"/><smm state="off"/><vmport state="off"/></features>
      <cpu mode="host-passthrough" check="none" migratable="off">
        <xsl:if test="@nested != 'true'">
          <feature policy="disable" name="svm"/>
        </xsl:if>
      </cpu>
      <clock offset="utc"/>
      <devices>
        <emulator>/run/libvirt/nix-emulators/qemu-system-x86_64</emulator>
        <xsl:for-each select="cfg:disk">
          <disk type="file" device="disk">
            <driver name="qemu" type="qcow2" iommu="on"/>
            <source file="{@src}"/>
            <target dev="{@dst}" bus="virtio"/>
          </disk>
        </xsl:for-each>
        <xsl:for-each select="cfg:net">
          <interface type="user">
            <xsl:if test="@dev"><source dev="{@dev}"/></xsl:if>
            <model type="virtio"/>
            <driver iommu="on"/>
            <rom enabled="no"/>
            <address type="pci" domain="0x0000" bus="{@bus}" slot="0x00" function="0x0"/>
            <backend type="passt"/>
            <xsl:for-each select="cfg:forward">
              <portForward proto="tcp"><range start="{@host}" to="{@guest}"/></portForward>
            </xsl:for-each>
          </interface>
        </xsl:for-each>
        <xsl:if test="@ui = 'true'">
          <input type="mouse" bus="ps2"/>
          <input type="keyboard" bus="ps2"/>
          <graphics type="spice" autoport="yes"><listen type="address"/><image compression="off"/><gl enable="no"/></graphics>
          <video><model type="virtio" heads="1" primary="yes"><acceleration accel3d="no"/></model></video>
        </xsl:if>
        <xsl:if test="@gpu = 'true'">
          <hostdev mode="subsystem" type="pci" managed="yes">
            <source><address domain="0x0000" bus="0x41" slot="0x00" function="0x0"/></source>
          </hostdev>
          <hostdev mode="subsystem" type="pci" managed="yes">
            <source><address domain="0x0000" bus="0x41" slot="0x00" function="0x1"/></source>
          </hostdev>
        </xsl:if>
        <audio id="1" type="none"/>
        <watchdog model="itco" action="reset"/>
        <memballoon model="none"/>
        <rng model="virtio"><driver iommu="on"/><backend model="random">/dev/urandom</backend></rng>
        <xsl:if test="@vsock = 'true'">
          <vsock model="virtio"><cid>auto</cid></vsock>
        </xsl:if>
        <xsl:for-each select="cfg:mount">
          <filesystem type="mount">
            <driver type="virtiofs"/>
            <source dir="{@src}"/>
            <target dir="{@dst}"/>
            <xsl:if test="@readonly"><readonly/></xsl:if>
          </filesystem>
        </xsl:for-each>
      </devices>
      <xsl:if test="@hardened = 'true'">
        <launchSecurity type="sev"><policy>0x000f</policy><cbitpos>47</cbitpos><reducedPhysBits>1</reducedPhysBits></launchSecurity>
      </xsl:if>
    </domain>
  </xsl:template>

  <vm xmlns="urn:vm-config" name="hermes" cpu="64" ram="128" ui="true" gpu="true" vsock="true" kernel="/ssd/vm/vm-r14-nvda-pods-BOOTX64.efi">
    <mount src="/ssd/internet" dst="/ssd/internet" readonly="true"/>
    <mount src="/hdd/internet/kiwix" dst="/hdd/internet/kiwix" readonly="true"/>
    <mount src="/hdd/internet/wikipedia" dst="/hdd/internet/wikipedia" readonly="true"/>
    <mount src="/ssd/vm/hermes" dst="/ssd/vm/hermes"/>
    <disk src="/ssd/vm/hermes.qcow2" dst="vda"/>
    <net dev="wg-hermes" bus="0x04">
      <forward host="2222" guest="22"/>
      <forward host="3000" guest="3000"/>
      <forward host="8000" guest="8000"/>
    </net>
  </vm>
</xsl:stylesheet>
