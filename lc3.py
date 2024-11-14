class LC3Simulator:
    def __init__(self):
        # Initialize registers (R0 to R7) and special registers (PC, CC)
        self.registers = [0] * 8  # 8 general-purpose registers
        self.registers[0] = 0xC1E0
        self.registers[1] = 0xD9B0
        self.registers[2] = 0xC338
        self.registers[3] = 0x7B13
        # self.registers[5] = 0x3001
        # self.registers[4] = 0x3007
        self.memory = [0] * 65536  # 64K memory (16-bit words)
        self.PC = 0  # Program Counter
        self.CC = 'Z'  # Condition Code (Z, N, P)
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
        elif opcode == 0x7:  # STR
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
        else:
            print(f"Unknown instruction {instruction:04X}")
            self.running = False

    def ADD(self, instruction):
        """ Handle the ADD instruction """
        dest = (instruction >> 9) & 0x7  # Destination register
        src1 = (instruction >> 6) & 0x7  # First source register
        imm_flag = (instruction >> 5) & 0x1  # Immediate mode flag
        
        if imm_flag == 1:  # Immediate mode
            imm5 = instruction & 0x1F  # 5-bit immediate value
            if imm5 & 0x10:  # Sign-extend if negative
                imm5 -= 0x20
            self.registers[dest] = self.registers[src1] + imm5
        else:  # Register mode
            src2 = instruction & 0x7  # Second source register
            self.registers[dest] = self.registers[src1] + self.registers[src2]
        
        self.update_CC(self.registers[dest])

    def AND(self, instruction):
        """ Handle the AND instruction """
        dest = (instruction >> 9) & 0x7  # Destination register
        src1 = (instruction >> 6) & 0x7  # First source register
        imm_flag = (instruction >> 5) & 0x1  # Immediate mode flag
        
        if imm_flag == 1:  # Immediate mode
            imm5 = instruction & 0x1F
            if imm5 & 0x10:  # Sign-extend if negative
                imm5 -= 0x20
            self.registers[dest] = self.registers[src1] & imm5
        else:  # Register mode
            src2 = instruction & 0x7  # Second source register
            self.registers[dest] = self.registers[src1] & self.registers[src2]
        
        self.update_CC(self.registers[dest])

    def NOT(self, instruction):
        """ Handle the NOT instruction """
        dest = (instruction >> 9) & 0x7  # Destination register
        src = (instruction >> 6) & 0x7  # Source register
        self.registers[dest] = ~self.registers[src] & 0xFFFF  # Ensure 16-bit result
        self.update_CC(self.registers[dest])

    def LD(self, instruction):
        """ Handle the LD (Load) instruction """
        dest = (instruction >> 9) & 0x7  # Destination register
        offset = instruction & 0x1FF  # 9-bit signed offset
        if offset & 0x100:  # Sign-extend
            offset -= 0x200
        address = self.PC + offset
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
        self.memory[address] = self.registers[src]

    def LDR(self, instruction):
        """ Handle the LDR (Load Register) instruction """
        dest = (instruction >> 9) & 0x7  # Destination register
        base = (instruction >> 6) & 0x7  # Base register
        offset = instruction & 0x3F  # 6-bit signed offset
        if offset & 0x20:  # Sign-extend
            offset -= 0x40
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
        address = self.registers[base] + offset
        self.memory[address] = self.registers[src]

    def LEA(self, instruction):
        """ Handle the LEA (Load Effective Address) instruction """
        dest = (instruction >> 9) & 0x7  # Destination register
        offset = instruction & 0x1FF  # 9-bit signed offset
        if offset & 0x100:  # Sign-extend
            offset -= 0x200
        self.registers[dest] = self.PC + offset
        self.update_CC(self.registers[dest])

    def LDI(self, instruction):
        """ Handle the LDI (Load Immediate) instruction """
        dest = (instruction >> 9) & 0x7  # Destination register
        offset = instruction & 0x1FF  # 9-bit signed offset


    def BR(self, instruction):
        """ Handle the BR (Branch) instruction """
        cond = (instruction >> 9) & 0x7  # Condition codes
        offset = instruction & 0x1FF  # 9-bit signed offset
        if offset & 0x100:  # Sign-extend
            offset -= 0x200
        if ((cond & 0x4 and self.CC == 'N') or
            (cond & 0x2 and self.CC == 'Z') or
            (cond & 0x1 and self.CC == 'P')):
            self.PC += offset

    def JMP(self, instruction):
        print("JMP")
        """ Handle the JMP (Jump) instruction """
        base = (instruction >> 6) & 0x7  # Base register
        self.PC = self.registers[base]

    def JSR(self, instruction):
        print("JSR")
        """ Handle the JSR (Jump to Subroutine) instruction """
        self.registers[7] = self.PC  # Link register (R7)

        use_offset = (instruction >> 11) & 0x1  # Link flag
        if use_offset:
            offset = instruction & 0x7FF  # 11-bit signed offset
            if offset & 0x400:  # Sign-extend
                offset -= 0x800
            self.PC += offset
        else:
            baseR = (instruction >> 6) & 0x7
            self.PC = self.registers[baseR]
            

    def TRAP(self, instruction):
        """ Handle the TRAP instruction (system calls) """
        trap_vector = instruction & 0xFF
        if trap_vector == 0x25:
            self.running = False
        self.PC = trap_vector  # Jump to the trap vector

    def update_CC(self, value):
        """ Update the Condition Codes based on the value """
        if value == 0:
            self.CC = 'Z'  # Zero
        elif value < 0:
            self.CC = 'N'  # Negative
        else:
            self.CC = 'P'  # Positive

    def run(self):
        """ Run the LC-3 program """
        while self.running:
            instruction = self.fetch()
            print(f"pc: {self.PC:04X}, instruction: {instruction:016b}")
            self.decode_execute(instruction)

        # When halted, show state of registers
        self.print_registers()

    def print_registers(self):
        """ Print the state of all registers """
        print("Registers:")
        for i in range(8):
            print(f"R{i}: {self.registers[i]:04X}")
        print(f"PC: {self.PC:04X}, CC: {self.CC}")
        print("\n")

    def inspect_memory(self, address):
        """ Inspect a specific memory address """
        print(f"Memory[{address:04X}]: {self.memory[address]:04X}")

program = [
    0x3000,  # orig x3000
    # 0b0001_001_001_1_00001, # ADD R1 R1 1
    # 0b0001_010_001_000_001, # ADD R2 R1 R1
    # 0b0000_110_000000011, # BR P +3
    # 0b0101_111_001_1_11111, # AND R7 R1 xFFFF
    # 0b1001_110_010_111111, # NOT R6 R2
    # 0b1110_011_111111111, # LEA R3 -1
    
    0xF025,  # HALT
]

simulator = LC3Simulator()
simulator.load_program(program)
simulator.run()

start = int(program[0])
for i in range(1, len(program)+1):
    mem = simulator.memory[start + i - 1]
    print(f"0x{start+i-1:04X}: {mem:04X}")

# def get_user_input():
#     program = []
#     print("Enter the LC-3 program. You can input instructions as binary (e.g., 0001001000100000) or hex (e.g., 0x1220).")
#     print("Type 'done' when you are finished.")
    
#     while True:
#         user_input = input("Instruction: ").strip().lower()
#         if user_input == "done":
#             break
#         try:
#             # Check if the user entered binary or hex
#             if user_input.startswith('0x') or user_input.startswith('0X'):
#                 # Hexadecimal input
#                 instruction = int(user_input, 16)
#             elif all(c in '01' for c in user_input) and len(user_input) == 16:
#                 # Binary input (must be 16-bits)
#                 instruction = int(user_input, 2)
#             else:
#                 print("Invalid input. Please enter a valid 16-bit binary or hex instruction.")
#                 continue

#             program.append(instruction)
#         except ValueError:
#             print("Invalid input. Please enter a valid 16-bit binary or hex instruction.")

#     return program


# def main():
#     # Get program input from the user
#     program = get_user_input()
    
#     # Reprint the program
#     print("\nProgram loaded:")
#     for i, instruction in enumerate(program):
#         print(f"Line {i + 1}: {instruction:04X}")
    
#     # Initialize and run the simulator
#     simulator = LC3Simulator()
#     simulator.load_program(program)
#     simulator.run()
    
#     # Ask user if they want to inspect registers or memory
#     while True:
#         user_choice = input("Would you like to inspect (1) the registers or (2) a specific memory address? (Enter 1 or 2, or 'done' to exit): ").strip().lower()
#         if user_choice == "1":
#             simulator.print_registers()
#         elif user_choice == "2":
#             try:
#                 address = int(input("Enter the memory address to inspect (in hex, e.g., 0x3000): "), 16)
#                 simulator.inspect_memory(address)
#             except ValueError:
#                 print("Invalid address. Please enter a valid hex address.")
#         elif user_choice == "done":
#             break
#         else:
#             print("Invalid option. Please enter 1, 2, or 'done'.")


# if __name__ == "__main__":
#     main()
