def merge_minterms(minterm1: str, minterm2: str) -> str:
    merged_minterm = ""
    for i in range(len(minterm1)):
        if minterm1[i] == minterm2[i]:
            merged_minterm += minterm1[i]
        else:
            merged_minterm += '-'
    return merged_minterm

def check_dashes_align(minterm1: str, minterm2: str) -> bool:
    for i in range(len(minterm1)):
        if minterm1[i] != '-' and minterm2[i] == '-':
            return False
        elif minterm1[i] == '-' and minterm2[i] != '-':
            return False
    return True

def check_minterm_differences(minterm1: str, minterm2: str) -> bool:
    m1 = int(''.join('0' if c == '-' else c for c in minterm1), 2)
    m2 = int(''.join('0' if c == '-' else c for c in minterm2), 2)
    res = m1 ^ m2

    return res != 0 and (res & (res - 1)) == 0

def get_prime_implicants(minterms: list[str]) -> list[str]:
    prime_implicants = []
    merges = [False for _ in minterms]
    number_of_merges = 0
    merged_minterm = ""
    minterm1 = ""
    minterm2 = ""

    for i in range(len(minterms)):
        for c in range(i+1, len(minterms)):
            minterm1 = minterms[i]
            minterm2 = minterms[c]
            
            if check_dashes_align(minterm1, minterm2) and check_minterm_differences(minterm1, minterm2):
                merged_minterm = merge_minterms(minterm1, minterm2)

                if merged_minterm not in prime_implicants:
                    prime_implicants.append(merged_minterm)
                number_of_merges+=1
                merges[i] = True
                merges[c] = True
    
    for j in range(len(minterms)):
        if not merges[j] and minterms[j] not in prime_implicants:
            prime_implicants.append(minterms[j])
    
    if number_of_merges > 0:
        return get_prime_implicants(prime_implicants)
    else:
        return prime_implicants

def convert_to_regular_expression(prime_implicant: str) -> str:
    regular_expression = ""
    for i in range(len(prime_implicant)):
        if prime_implicant[i] == '-':
            regular_expression += "\\d"
    return regular_expression

def create_prime_implicant_chart(prime_implicants: list[str], minterms: list[str]) -> dict[str, list[str]]:
    prime_implicant_chart = {}
    for i in range(len(prime_implicants)):
        prime_implicant_chart[prime_implicants[i]] = []
    
    for i in range(len(prime_implicant_chart.keys())):
        prime_implicant = list(prime_implicant_chart.keys())[i]

        # regular_expression = convert_to_regular_expression(prime_implicant)
        for j in range(len(minterms)):
            # print(minterms[j])
            failed = False
            for k in range(len(minterms[j])):
                # print(minterms[j][k])
                # print(prime_implicant[k])
                if prime_implicant[k] == '-':
                    continue
                minterm = minterms[j][k]
                if (minterm != prime_implicant[k]):
                    failed = True
                    break
            if not failed:
                prime_implicant_chart[prime_implicant].append(True)
            else:
                prime_implicant_chart[prime_implicant].append(False)
            # print(f"minterm: {minterms[j]} | regex: {regular_expression} | prime_implicant: {prime_implicant}")
    # print(prime_implicant_chart)
    return prime_implicant_chart

def find_valid_combinations(coverage_dict):
    # Get all possible implicant combinations
    implicants = list(coverage_dict.keys())
    num_columns = len(list(coverage_dict.values())[0])
    valid_solutions = []
    
    # Try every possible combination of 3 implicants
    # (we know we need at least 3 for full coverage in this case)
    for i in range(len(implicants)):
        for j in range(i + 1, len(implicants)):
            for k in range(j + 1, len(implicants)):
                # Get the three implicants to test
                imp1 = implicants[i]
                imp2 = implicants[j]
                imp3 = implicants[k]
                
                # Check if this combination covers all columns
                is_valid = True
                for col in range(num_columns):
                    # If any column isn't covered, this combination is invalid
                    if not (coverage_dict[imp1][col] or 
                           coverage_dict[imp2][col] or 
                           coverage_dict[imp3][col]):
                        is_valid = False
                        break
                
                # If we found a valid combination, add it to solutions
                if is_valid:
                    valid_solutions.append([imp1, imp2, imp3])
    
    return valid_solutions

minterms = [
    {
        'binary': "0100",
        'required': True,
    },
    {
        'binary': "1000",
        'required': True,
    },
    {
        'binary': "1001",
        'required': False,
    },
    {
        'binary': "1010",
        'required': True,
    },
    {
        'binary': "1100",
        'required': True,
    },
    {
        'binary': "1011",
        'required': True,
    },
    {
        'binary': "1110",
        'required': False,
    },
    {
        'binary': "1111",
        'required': True
    }
]

# minterms = [
#     "0100",
#     "1000",
#     "1001",
#     "1010",
#     "1100",
#     "1011",
#     "1110",
#     "1111",

pm_implicants = sorted(
    [minterm['binary'] for minterm in minterms if minterm['required']], 
    key=lambda x: int(x, 2)
)
# pm_implicants = result
# print(pm_implicants)
# pm_implicants = [q['binary'] for q in minterms if q['required']]
all_implicants = [q['binary'] for q in minterms]
prime_implicants = get_prime_implicants(all_implicants)
pi_chart = create_prime_implicant_chart(prime_implicants, pm_implicants)
# print(get_prime_implicants(minterms))

result = find_valid_combinations(pi_chart)

print(result)

# merge_minterms([1, 2, 3], [4, 5, 6])