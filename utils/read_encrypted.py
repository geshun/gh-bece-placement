import cryptography.fernet as cf
import io
import pandas
import zipfile


def read_encrypted(file, key):
    """A function for reading the encrypted file. File could be zipped

    Args:
        file (str): path (as character string) to the location of the file
        key (bytes): key (as byte string) acceptable by Fernet encryption

    Returns:
        Pandas.DataFrame: Pandas dataframe of the data in the encrypted file
    """
    if file.endswith(".zip"):
        with zipfile.ZipFile(file, "r") as z:
            encrypted = z.read(z.namelist()[0])
    else:
        with open(file, "rb") as f:
            encrypted = f.read()

    decrypted = cf.Fernet(key).decrypt(encrypted)
    df = pandas.read_csv(io.BytesIO(decrypted))

    return df


if __name__ == "__main__":
    import getpass
    df = read_encrypted("data/bece-encrypted.zip",
                        bytes(getpass.getpass("Enter key: "), "utf-8"))
    print(df)
