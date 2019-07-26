"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 0x08
        # holds 255 bytes
        self.ram = [0] * 0xff
        #Program Counter, address of the currently executing instruction
        self.pc = 0x00 
        #Instruction Register, contains a copy of the currently executing instruction
        self.ir = 0x00
        self.reg[7] = 0xf4
        self.start = self.reg[7]
        #flag for conditionals
        self.flag = 0b0000000
        #opcodes
        self.cpu_run = True
        self.h = 0b00000001 
        self.ldi = 0b10000010
        self.prn = 0b01000111
        self.mul = 0b10100010
        self.push = 0b01000101
        self.pop = 0b01000110
        self.call = 0b01010000
        self.ret = 0b00010001
        self.add = 0b10100000
        self.cmp = 0b10100111
        self.jmp = 0b01010100
        self.jeq = 0b01010101
        self.jne = 0b01010110
        self.op_table = {}
        self.op_table[self.h] = self.cpu_halt
        self.op_table[self.ldi] = self.cpu_ldi
        self.op_table[self.prn] = self.cpu_prn
        self.op_table[self.mul] = self.cpu_mul
        self.op_table[self.push] = self.cpu_push
 
    def cpu_halt(self):
        self.cpu_run = False
        sys.exit(1)  

    def cpu_ldi(self):
        o1 = self.ram_read(self.pc + 1)
        o2 = self.ram_read(self.pc + 2)
        self.ram[o1] = o2
        self.pc += 3
    
    def cpu_prn(self):
        print(self.reg[self.pc + 1])
        self.pc += 2 

    def cpu_mul(self):
        pass

    def cpu_push(self):
        self.start -= 1
        reg_num = self.ram[self.pc + 1]
        value = self.reg[reg_num]
        self.ram[self.start] = value
        
    
    def cpu_pop(self):
        value = self.ram[self.start]
        reg_num = self.ram[self.pc + 1]
        self.reg[reg_num] = value
        self.start += 1
        
    
    def cpu_call(self):
        return_addr = self.pc + 2
        self.start -= 1
        self.ram[self.start] = return_addr

        reg_num = self.ram[self.pc + 1]
        sub_add = self.reg[reg_num]
        self.pc = sub_add
    
    def cpu_ret(self):
        ret_add = self.ram[self.start]
        self.start += 1
        self.pc = ret_add
    
    def cpu_cmp(self):
        pass
    
    def cpu_jmp(self):
        reg_num = self.ram_read(self.pc + 1)
        self.pc = self.reg[reg_num]
    
    def cpu_jeq(self):
        if self.flag == 0b00000001:
            reg_num = self.ram_read(self.pc + 1)
            self.pc = self.reg[reg_num]
        else:
            self.pc += 2
            
    
    def cpu_jne(self):
        if self.flag != 0b00000001:
            reg_num = self.ram_read(self.pc + 1)
            self.pc = self.reg[reg_num]
        else:
            self.pc += 2


    def ram_read(self, current):
        return self.ram[current]

    def ram_write(self, write, current):
        self.ram[current] = write

    def load(self):
        """Load a program into memory."""

        if len(sys.argv) != 2:
            print(f"usage: {sys.argv[0]} filename")
            sys.exit(1)

        try:
             with open(sys.argv[1]) as f:
                address = 0
                for line in f:
                    num = line.split("#", 1)[0]

                    if num.strip() == '':  # ignore comment-only lines
                        continue

                    # print(int(num, 2))
                    self.ram[address] = int(num, 2)
                    address += 1

        except FileNotFoundError:
            print(f"{sys.argv[0]}: {sys.argv[1]} not found")
            sys.exit(2)


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "CMP":
            result = self.reg[reg_b] - self.reg[reg_a]
            if result > 0:
                #a is less than b
                self.flag = 0b00000100
            elif result < 0:
                #a is more than b
                self.flag = 0b00000010
                pass
            elif result == 0:
                #a is equal b
                self.flag = 0b00000001
            else:
                self.flag = 0b00000000
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 3),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        LDI = 0b10000010
        PRN = 0b01000111
        MUL = 0b10100010
        PUSH = 0b01000101
        POP = 0b01000110
        CALL = 0b01010000
        RET = 0b00010001
        ADD = 0b10100000
        CMP = 0b10100111
        JMP = 0b01010100
        JEQ = 0b01010101
        JNE = 0b01010110

        
        # self.trace()
        run_cpu = True

        while run_cpu:
            self.ir = self.pc
            o1 = self.ram_read(self.pc + 1)
            o2 = self.ram_read(self.pc + 2)

            if self.ram[self.ir] == self.h:
                run_cpu = False
            elif self.ram[self.ir] == LDI:
                self.reg[o1] = o2
                self.pc += 3
            elif self.ram[self.ir] == PRN:
                print(self.reg[o1])
                self.pc += 2
            elif self.ram[self.ir] == ADD:
                self.alu("ADD", o1, o2)
                self.pc += 3
            elif self.ram[self.ir] == MUL:
                self.alu("MUL", o1, o2)
                self.pc += 3
            elif self.ram[self.ir] == PUSH:
                self.cpu_push()
                self.pc += 2
            elif self.ram[self.ir] == POP:
                self.cpu_pop()
                self.pc += 2
            elif self.ram[self.ir] == CALL:
                self.cpu_call()
            elif self.ram[self.ir] == RET:
                self.cpu_ret()
            elif self.ram[self.ir] == CMP:
                self.alu("CMP", o1, o2)
                self.pc += 3
            elif self.ram[self.ir] == JMP:
                self.cpu_jmp()   
            elif self.ram[self.ir] == JEQ:
                self.cpu_jeq()   
            elif self.ram[self.ir] == JNE:
                self.cpu_jne()
                


