class LC3Simulator:
    def __init__(self):
        # Initialize registers (R0 to R7) and special registers (PC, CC)
        self.registers = [0] * 8  # 8 general-purpose registers

        self.memory = [0] * 65536  # 64K memory (16-bit words)
        self.PC = 0x3000
        self.ADDR = 0x3000
        self.CC = 'Z'  # Condition Code (N, Z, P)
        self.running = True

    def load_program(self, program):
        """ Load a list of 16-bit instructions into memory """
        mem_start = int(program[0])
        self.PC = mem_start
        for i in range(1, len(program)):
            self.memory[mem_start + i - 1] = program[i]

    def fetch(self):
        """ Fetch the instruction at the current PC and increment PC """
        # print(f"PC: {self.PC}")
        # throw error 
        instruction = self.memory[self.PC]
        # print(f"instruction: {instruction}")
        # test = 5 / 0
        self.PC += 1
        return instruction

    def decode_execute(self, instruction):
        """ Decode and execute the instruction """
        opcode = (instruction >> 12) & 0xF  # Extract the opcode (4 MSB)
        # print(f"opcode: {opcode:04X}")
        if opcode == 0x1:  # ADD
            self.ADD(instruction)
        elif opcode == 0x5:  # AND
            self.AND(instruction)
        elif opcode == 0x9:  # NOT
            self.NOT(instruction)
        elif opcode == 0x2:  # LD
            self.LD(instruction)
        elif opcode == 0x3:  # ST
            self.ST(instruction)
        elif opcode == 0x6:  # LDR
            self.LDR(instruction)
        elif opcode == 0x7:  # ST
            self.STR(instruction)
        elif opcode == 0xE:  # LEA
            self.LEA(instruction)
        elif opcode == 0x0:  # BR (Branch)
            self.BR(instruction)
        elif opcode == 0xC:  # JMP
            self.JMP(instruction)
        elif opcode == 0x4:  # JSR
            self.JSR(instruction)
        elif opcode == 0xF:  # TRAP
            self.TRAP(instruction)
        elif opcode == 0xF:  # HALT
            self.running = False
        elif opcode == 0xA:
            self.LDI(instruction)
        elif opcode == 0xB:
            self.STI(instruction)
        else:
            print("Unknown instruction {:04X}".format(instruction))
            self.running = False

    def ADD(self, instruction):
        """ Handle the ADD instruction """
        dest = (instruction >> 9) & 0x7  # Destination register
        src1 = (instruction >> 6) & 0x7  # First source register
        imm_flag = (instruction >> 5) & 0x1  # Immediate mode flag

        print("ADD R{} <- R{} + ".format(dest, src1), end="")
        if imm_flag == 1:  # Immediate mode
            imm5 = instruction & 0x1F  # 5-bit immediate value
            if imm5 & 0x10:  # Sign-extend if negative
                imm5 -= 0x20
            self.registers[dest] = self.registers[src1] + imm5
            print("#{:d}".format(imm5))
        else:  # Register mode
            src2 = instruction & 0x7  # Second source register
            self.registers[dest] = self.registers[src1] + self.registers[src2]
            print("R{}".format(src2))
        
        self.update_CC(self.registers[dest])

    def AND(self, instruction):
        """ Handle the AND instruction """
        dest = (instruction >> 9) & 0x7  # Destination register
        src1 = (instruction >> 6) & 0x7  # First source register
        imm_flag = (instruction >> 5) & 0x1  # Immediate mode flag
        
        print("AND R{} <- R{} & ".format(dest, src1), end="")

        if imm_flag == 1:  # Immediate mode
            imm5 = instruction & 0x1F
            if imm5 & 0x10:  # Sign-extend if negative
                imm5 -= 0x20
            self.registers[dest] = self.registers[src1] & imm5
            print("#{:d}".format(imm5))
        else:  # Register mode
            src2 = instruction & 0x7  # Second source register
            self.registers[dest] = self.registers[src1] & self.registers[src2]
            print("R{}".format(src2))
        self.update_CC(self.registers[dest])

    def NOT(self, instruction):
        """ Handle the NOT instruction """
        dest = (instruction >> 9) & 0x7  # Destination register
        src = (instruction >> 6) & 0x7  # Source register

        print("NOT R{} <- R{}".format(dest, src))
        
        self.registers[dest] = ~self.registers[src] & 0xFFFF  # Ensure 16-bit result
        self.update_CC(self.registers[dest])

    def LD(self, instruction):
        """ Handle the LD (Load) instruction """
        dest = (instruction >> 9) & 0x7  # Destination register
        offset = instruction & 0x1FF  # 9-bit signed offset
        if offset & 0x100:  # Sign-extend
            offset -= 0x200
        address = self.PC + offset

        print("LD R{} <- M[{:04X}]".format(dest, address))

        self.registers[dest] = self.memory[address]
        self.update_CC(self.registers[dest])

    def ST(self, instruction):
        """ Handle the ST (Store) instruction """
        src = (instruction >> 9) & 0x7  # Source register
        offset = instruction & 0x1FF  # 9-bit signed offset
        # print(f"offset: {self.PC + offset:04X}")
        if offset & 0x100:  # Sign-extend
            offset -= 0x200
        address = self.PC + offset
        
        print("ST M[{:04X}] <- R{}".format(address, src))
        
        self.memory[address] = self.registers[src]

    def LDR(self, instruction):
        """ Handle the LDR (Load Register) instruction """
        dest = (instruction >> 9) & 0x7  # Destination register
        base = (instruction >> 6) & 0x7  # Base register
        offset = instruction & 0x3F  # 6-bit signed offset
        if offset & 0x20:  # Sign-extend
            offset -= 0x40
        
        print("LDR R{} <- M[R{} + #{:d}]".format(dest, base, offset))
        
        address = self.registers[base] + offset
        self.registers[dest] = self.memory[address]
        self.update_CC(self.registers[dest])

    def STR(self, instruction):
        """ Handle the STR (Store Register) instruction """
        src = (instruction >> 9) & 0x7  # Source register
        base = (instruction >> 6) & 0x7  # Base register
        offset = instruction & 0x3F  # 6-bit signed offset
        if offset & 0x20:  # Sign-extend
            offset -= 0x40

        print("STR M[R{} + #{:d}] <- R{}".format(base, offset, src))

        address = self.registers[base] + offset
        self.memory[address] = self.registers[src]

    def LEA(self, instruction):
        """ Handle the LEA (Load Effective Address) instruction """
        dest = (instruction >> 9) & 0x7  # Destination register
        offset = instruction & 0x1FF  # 9-bit signed offset
        if offset & 0x100:  # Sign-extend
            offset -= 0x200

        print("LEA R{} <- {:04X} + #{:d}]".format(dest, self.PC, offset))

        self.registers[dest] = self.PC + offset
        self.update_CC(self.registers[dest])

    def LDI(self, instruction):
        """ Handle the LDI (Load Immediate) instruction """
        dest = (instruction >> 9) & 0x7  # Destination register
        offset = instruction & 0x1FF  # 9-bit signed offset
        if offset & 0x100:  # Sign-extend
            offset -= 0x200

        print("LDI R{} <- M[M[{:04X} + #{:d}]]".format(dest, self.PC, offset))

        temp_address = self.PC + offset
        final_address = self.memory[temp_address]
        self.registers[dest] = self.memory[final_address]
        self.update_CC(self.registers[dest])

    def STI(self, instruction):
        """ Handle the STI (Store Immediate) instruction """
        source = (instruction >> 9) & 0x7  # Destination register
        offset = instruction & 0x1FF  # 9-bit signed offset

        if offset & 0x100:  # Sign-extend
            offset -= 0x200

        print("STI M[M[{:04X} + #{:d}]] <- R{}".format(self.PC, offset, source))

        temp_address = self.PC + offset
        final_address = self.memory[temp_address]
        self.memory[final_address] = self.registers[source]

    def BR(self, instruction):
        # print("BR")
        """ Handle the BR (Branch) instruction """
        cond = (instruction >> 9) & 0x7  # Condition codes
        offset = instruction & 0x1FF  # 9-bit signed offset
        if offset & 0x100:  # Sign-extend
            offset -= 0x200

        print("BR{:03b} PC <- PC + #{:d}".format(cond, offset), end="")

        if ((cond & 0x4 and self.CC == 'N') or
            (cond & 0x2 and self.CC == 'Z') or
            (cond & 0x1 and self.CC == 'P')):
            self.PC += offset
            print(":T")
        else:
            print(":F")

    def JMP(self, instruction):
        """ Handle the JMP (Jump) instruction """
        base = (instruction >> 6) & 0x7  # Base register
        print("JMP PC <- R{}".format(base))
        self.PC = self.registers[base]

    def JSR(self, instruction):
        print("JSR")
        """ Handle the JSR (Jump to Subroutine) instruction """
        self.registers[7] = self.PC  # Link register (R7)

        print("JSR PC <- {:04X} + ".format(self.PC), end="")

        use_offset = (instruction >> 11) & 0x1  # Link flag
        if use_offset:
            offset = instruction & 0x7FF  # 11-bit signed offset
            if offset & 0x400:  # Sign-extend
                offset -= 0x800
            self.PC += offset
            print("#{:d}]".format(offset))
        else:
            baseR = (instruction >> 6) & 0x7
            self.PC = self.registers[baseR]
            print("R{}".format(baseR))
            

    def TRAP(self, instruction):
        """ Handle the TRAP instruction (system calls) """
        trap_vector = instruction & 0xFF
        if trap_vector == 0x25:
            self.running = False
        print("TRAP {:04X}".format(trap_vector))
        self.PC = trap_vector  # Jump to the trap vector

    def update_CC(self, value):
        """ Update the Condition Codes based on the value """
        if value == 0:
            self.CC = 'Z'  # Zero
        elif ((value >> 15) & 0x1) == 1:
            self.CC = 'N'  # Negative
        else:
            self.CC = 'P'  # Positive

    def run(self):
        """ Run the LC-3 program """
        skip = "2" == input("Enter...\n[1] to go step by step\n[2] to skip steps\n")
        print("Enter [2] to stop execution at any time")
        
        program_addr = 0
        
        self.ADDR = self.PC

        while self.running:
            instruction = self.fetch()
            print("{:04X}:{:04X} ".format(self.ADDR, instruction), end="")

            if skip == False:
                inp = input("")
                if "2" == inp:
                    self.running = False
                    break
                elif "3" == inp:
                    self.debug()

            else:
                print("")

            if instruction == 0:
                print("Done!")
                self.PC = self.ADDR
                break
            self.decode_execute(instruction)
            program_addr += 1
            self.ADDR = self.PC

        # When halted, show state of registers
        self.debug()
        self.print_registers()

    def debug(self):
        while True:
            inp = input("")
            inp = inp.strip().lower().replace(" ", "")
            if "1" == inp:
                self.print_registers()
            elif "2" == inp: 
                self.print_memory(self.ADDR)
            elif (inp.startswith("i")):
                inp = inp.replace("i", "")
                if len(inp) == 16:
                    self.print_memory(int(inp, 2))
                elif len(inp) == 4:
                    self.print_memory(int(inp, 16))
            elif len(inp) == 16:
                self.inspect_memory(int(inp, 2))
            elif len(inp) == 4:
                self.inspect_memory(int(inp, 16))
            elif "3" == inp:
                break
            else:
                break

    def print_registers(self):
        """ Print the state of all registers """
        print("Registers:")
        for i in range(0,8,2):
            register_one = self.registers[i]
            register_two = self.registers[i+1]
            print("R{}:{:04X} R{}:{:04X}".format(i, register_one, i+1, register_two))
        # print(f"PC: {self.PC:04X}  CC: {self.CC}")
        print("PC:{:04X}  CC:{}".format(self.PC, self.CC))
        # print("\n")

    def print_memory(self, addr, length=4):
        print("Memory:")
        try:
            for i in range(addr - length, addr + length, 2):
                curr_addr = i
                curr_val = self.memory[curr_addr]
                next_addr = curr_addr + 1
                next_val = self.memory[next_addr]
                print("{curr_addr:04X}:{curr_val:04X} {next_addr:04X}:{next_val:04X}".format(curr_addr=curr_addr, curr_val=curr_val, next_addr=next_addr, next_val=next_val))
        except IndexError:
            print("Out of Bounds")

    def inspect_memory(self, address):
        """ Inspect a specific memory address """
        print("{:04X}:{:04X}".format(address, self.memory[address]))

simulator = LC3Simulator()

def request_initial_state():
    addr = input("Enter Start Addr\n")
    addr = addr.strip().lower().replace(" ", "")
    
    if len(addr) == 4:
        addr = int(addr, 16)
    elif len(addr) == 16:
        addr = int(addr, 2)
    else:
        addr = 0x3000

    
    print("starting addr: {:04X}".format(addr))
    simulator.PC = addr

    while True:
        inp = input("{:04X}:".format(addr))
        inp = inp.strip().lower().replace(" ", "")
        if  "3" == inp:
            break
        elif len(inp) == 16:
            # program.append(int(inp, 2))
            simulator.memory[addr] = int(inp, 2)
            print("0x{:04X}".format(int(inp, 2)))
            addr += 1
        elif len(inp) == 4:
            simulator.memory[addr] = int(inp, 16)
            print("0x{:016b}".format(int(inp, 16)))
            addr += 1
        elif len(inp) == 20:
            new_addr = inp[0:4]
            new_val = inp[4:20]
            addr = int(new_addr, 16)
            simulator.memory[addr] = int(new_val, 2)
            print("0x{:04X}".format(int(new_val, 2)))
            addr += 1
        elif len(inp) == 8:
            new_addr = inp[0:4]
            new_val = inp[4:8]
            addr = int(new_addr, 16)
            simulator.memory[addr] = int(new_val, 16)
            print("0x{:016b}".format(int(new_val, 16)))
            addr += 1
        else:
            continue
    
    print("Memory Done!\nNow enter Registers")
    while True:
        inp = input("Enter Registers \n")
        inp = inp.strip().lower().replace(" ", "")
        if  "3" == inp:
            break
        elif len(inp) == 17:
            register = inp[0]
            value = inp[1:17]
            simulator.registers[int(register)] = int(value, 2)
            print("R{} <- 0x{:04X}".format(int(register), int(value, 2)))
        elif len(inp) == 5:
            register = inp[0]
            value = inp[1:5]
            simulator.registers[int(register)] = int(value, 16)
            print("R{} <- 0x{:016b}".format(int(register), int(value, 16)))
        
    simulator.print_registers()
    
# if __name__ == "__main__":
request_initial_state()
simulator.run()