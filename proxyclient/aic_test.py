#!/usr/bin/python
from setup import *
import asm

ULCON = 0x235200000
UCON = 0x235200004
UFCON = 0x235200008
UTRSTAT = 0x235200010

AIC = 0x23b100000
AIC_TB = 0x23b108000
AIC_TGT_DST = AIC + 0x3000
AIC_SW_GEN_SET = AIC + 0x4000
AIC_SW_GEN_CLR = AIC + 0x4080
AIC_MASK_SET = AIC + 0x4100
AIC_MASK_CLR = AIC + 0x4180
AIC_HW_STATE = AIC + 0x4200

AIC_INTERRUPT_ACK = AIC + 0x2004
AIC_IPI_SET = AIC + 0x2008
AIC_IPI_CLR = AIC + 0x200c

AIC_IPI_MASK_SET = AIC + 0x2024
AIC_IPI_MASK_CLR = AIC + 0x2028

daif = u.mrs(DAIF)
print("DAIF: %x" % daif)
daif &= ~0x3c0
#daif |= 0x3c0
u.msr(DAIF, daif)
print("DAIF: %x" % u.mrs(DAIF))

def cpoll():
    mon.poll()
    print("<")
    mon.poll()
    print(">")

p.memset32(AIC_MASK_SET, 0xffffffff, 0x80)
p.memset32(AIC_SW_GEN_CLR, 0xffffffff, 0x80)
p.memset32(AIC_TGT_DST, 1, 0x1000)

#mon.add(AIC + 0x0000, 0x100)
#mon.add(AIC + 0x1000, 0x100)
#mon.add(AIC + 0x2008, 0x0f8)
#mon.add(AIC + 0x3000, 0x400)
#mon.add(AIC + 0x4000, 0x400)
#mon.add(AIC + 0x8000, 0x20)
#mon.add(AIC + 0x8030, 0xd0)
mon.add(0x235200000, 0x20)

def test_ipi():
    cpoll()

    print("Set IPI")

    p.write32(AIC_IPI_SET, 1)

    cpoll()
    cpoll()

    print("Read ACK reg")

    reason = p.read32(AIC_INTERRUPT_ACK)
    print("reason: 0x%x" % reason)

    cpoll()

    print("Write reason")
    p.write32(AIC_INTERRUPT_ACK, reason)

    cpoll()

    reason = p.read32(AIC_INTERRUPT_ACK)
    print("reason: 0x%x" % reason)

    cpoll()

    print("Write ACK reg")
    p.write32(AIC_INTERRUPT_ACK, reason)
    cpoll()

    print("Clear IPI")

    p.write32(AIC_IPI_CLR, 1)
    cpoll()

    print("Read ACK reg")

    reason = p.read32(AIC_INTERRUPT_ACK)

    print("reason: 0x%x" % reason)

    cpoll()

    print("Write IPI ACK")

    p.write32(AIC_IPI_MASK_CLR, 1)

    cpoll()

def test_timer():
    cpoll()

    freq = u.mrs(CNTFRQ_EL0)
    print("Timer freq: %d" % freq)

    u.msr(CNTP_CTL_EL0, 0)
    u.msr(CNTP_TVAL_EL0, freq * 2)
    u.msr(CNTP_CTL_EL0, 1)

    iface.ttymode()

    #while True:
        #p.nop()
        #time.sleep(0.3)
        #print(". %x" % u.mrs(CNTP_CTL_EL0))

def get_irq_state(irq):
    v = p.read32(AIC_HW_STATE + 4* (irq//32))
    return bool(v & 1<<(irq%32))

def test_uart_irq():
    cpoll()
    #p.memset32(AIC_MASK_CLR, 0xffffffff, 0x80)

    print("cleanup")
    p.write32(UCON, 5)
    p.write32(UFCON, 0x11)
    p.write32(UTRSTAT, 0xfff)

    cpoll()

    for irq in range(600, 610):
        #print("S: ", get_irq_state(irq))
        p.write32(AIC_SW_GEN_CLR + 4* (irq//32), 1<<(irq%32))
        #print("S: ", get_irq_state(irq))
        #print("a")
        #print("S: ", get_irq_state(irq))
        p.write32(AIC_MASK_CLR + 4* (irq//32), 1<<(irq%32))
        #print("S: ", get_irq_state(irq))
        #print("b")

    irq = 605

    cpoll()
    print("a")
    print("S: ", get_irq_state(irq))
    print("ucon: %x" %p.read32(UCON))

    TX_IRQ_EN = 0x1000

    RX_IRQ_ENABLE = 0x20000
    RX_IRQ_UNMASK = 0x10000

    RX_IRQ_ENA = 0x20000
    RX_IRQ_MASK = 0x4000 # defer?

    code = u.malloc(0x1000)

    c = asm.ARMAsm("""
        ldr x1, =0x235200000

        ldr x3, =0xc000000
1:
        subs x3, x3, #1
        bne 1b
        mov x2, 'A'
        #str w2, [x1, #0x20]
        #str w2, [x1, #0x20]
        #str w2, [x1, #0x20]
        #str w2, [x1, #0x20]
        #str w2, [x1, #0x20]
        #str w2, [x1, #0x20]
        #str w2, [x1, #0x20]
        #str w2, [x1, #0x20]
        #str w2, [x1, #0x20]
        #str w2, [x1, #0x20]
        #str w2, [x1, #0x20]
        #str w2, [x1, #0x20]
        #str w2, [x1, #0x20]
        #str w2, [x1, #0x20]
        #str w2, [x1, #0x20]
        #str w2, [x1, #0x20]
        #str w2, [x1, #0x20]
        #str w2, [x1, #0x20]
        #str w2, [x1, #0x20]
        #str w2, [x1, #0x20]
        #str w2, [x1, #0x20]
        #str w2, [x1, #0x20]
        #str w2, [x1, #0x20]
        #str w2, [x1, #0x20]
        #str w2, [x1, #0x20]
        #str w2, [x1, #0x20]
        #str w2, [x1, #0x20]
        #str w2, [x1, #0x20]
        #str w2, [x1, #0x20]
        #str w2, [x1, #0x20]
        #str w2, [x1, #0x20]

        mov x3, #0x3ff
        str w3, [x1, #0x10]
        #str w2, [x1, #0x20]
        str w0, [x1, #4]
        ldr w0, [x1, #0x10]

        ldr x3, =0xc00000
1:
        subs x3, x3, #1
        bne 1b

        #mov x3, #0x3ff
        #str w3, [x1, #0x10]
        #ldr w2, [x1, #4]
        #mov x2, #0x205
        #str w2, [x1, #4]
        #str w0, [x1, #4]
        ##ldr w0, [x1, #0x10]

        #ldr x3, =0xc00000
#1:
        #subs x3, x3, #1
        #bne 1b

        ldr w0, [x1, #0x10]
        #mov w0, w2
        ret
""", code)
    iface.writemem(code, c.data)
    p.dc_cvau(code, len(c.data))
    p.ic_ivau(code, len(c.data))

    #RX_IRQ_

    """
UCON    UTRSTAT
00200           TX FIFO thresh IRQ delivery enable
00080   0200    TX FIFO threshold IRQ unmask
20000   0100    RX IRQ unmask
10000           RX IRQ delivery enable
"""

    # edge triggered
    TX_FIFO_THRESH_CROSSED_IRQ_UNMASK = 0x2000

    TX_IRQ_UNMASK = 0x200
    TX_EVENT_ENABLE = 0x80
    RX_EVENT_ENABLE = 0x20000
    RX_IRQ_UNMASK = 0x10000

    #flags = 0x7ffc0
    crash = 0x180000
    no_irqs = 0x21c5c0
    instant_irqs = 0x3a00
    #flags = no_irqs | 0x0000
    #flags = 0x2e5c0
    #flags = 0x2000

    #flags = 0x30000
    #flags = 0x80
    flags = 0x7ff80


    val = flags | 0x005
    #print("ucon<-%x" % val)
    #p.write32(UCON, val)
    p.write32(UTRSTAT, 0xfff)
    print("utrstat=%x" % p.read32(UTRSTAT))
    ret = p.call(code, val)
    print("utrstat::%x" % ret)
    print("utrstat=%x" % p.read32(UTRSTAT))
    time.sleep(0.5)
    iface.dev.write(b'1')
    #print(iface.dev.read(1))
    time.sleep(0.1)
    print("ucon: %x" %p.read32(UCON))
    print("delay")
    try:
        p.udelay(500000)
    except:
        pass
    iface.dev.write(bytes(64))
    p.nop()
    print("ucon: %x" %p.read32(UCON))
    print("S: ", get_irq_state(irq))

    #while True:
        #print("S: ", get_irq_state(irq))
        #p.write32(UTRSTAT, 0xfff)
        #print("utrstat=%x" % p.read32(UTRSTAT))
        #print("ucon: %x" %p.read32(UCON))
        #print(">S: ", get_irq_state(irq))
        #p.write32(UCON, flags | 0x005)
        #print(">ucon: %x" %p.read32(UCON))
        #time.sleep(0.1)





#test_ipi()
#test_timer()
test_uart_irq()
