def create_int_file(filename="pids.txt"):
    fakePids = [1, 2, 3, 4, 5]
    with open(filename, 'w') as file:
        for pid in fakePids:
            file.write(f"{pid}\n")
    
    print(f"File '{filename}' created successfully.")

if __name__ == "__main__":
    create_int_file()
