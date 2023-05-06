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


def clean_region(region):
    """Takes the region column of the BECE data frame and reconcile the values

    Args:
        region (Pandas Series): The raw region column

    Returns:
        Series: Cleaned column values
    """
    region = (
        region
        .str.title()
        .str.replace(" Region", "")
        .str.replace("Gr.", "Greater", regex=False)
        .str.replace("B.A.", "Brong-Ahafo", regex=False)
        .str.replace("U.", "Upper", regex=False)
    )
    return region


def clean_elective(elective):
    """To be used together with the `map` method of a series to 
        clean the best elective columns of the BECE data frame

    Args:
        elective (str): The raw string in the elective column

    Returns:
        str: A string with the correct replacement
    """
    mapping = {
        'B.D.T./PRE-TECH': 'BDT Pre-Tech.',
        'B.D.T/PRE-TECH': 'BDT Pre-Tech.',
        'BDT/PRE-TECH': 'BDT Pre-Tech.',
        'B.D.T./PRE-TECH.': 'BDT Pre-Tech.',
        'B.D.T./HOME ECONS.': 'BDT Home Econs.',
        'BDT/HOME ECONS': 'BDT Home Econs.',
        'REL.& MORAL EDUC.': 'Rel. & Moral Educ.',
        'REL.& MORAL EDUC': 'Rel. & Moral Educ.',
        'RME': 'Rel. & Moral Educ.',
        'INFO. & COMM.TECH.': 'Info. & Comm. Tech.',
        'ICT': 'Info. & Comm. Tech.',
        'B.D.T./VISUAL ARTS': 'BDT Visual Arts'
    }
    return mapping.get(elective, elective.title())


def clean_bece(df):
    """Cleans the raw BECE data frame by applying custom functions

    Args:
        df (Pandas DataFrame): The raw BECE data frame

    Returns:
        DataFrame: A clean data frame suitable for analysis
    """
    df = (
        df
        .assign(**{col: lambda df, col=col: df[col].str.title()
                   for col in ["dtrack", "jhs_type", "jhs_district", "shs_name"]})
        .assign(**{col: lambda df, col=col: df[col].map(clean_elective, na_action='ignore')
                   for col in ["best_elective_1_name", "best_elective_2_name"]})
        .assign(**{col: lambda df, col=col: df[col].astype("category")
                   for col in ["dtrack", "jhs_type", "gender"]})
        .assign(jhs_region=clean_region(df.jhs_region))
    )
    return df


if __name__ == "__main__":
    import getpass
    df = read_encrypted("data/bece-encrypted.zip",
                        bytes(getpass.getpass("Enter key: "), "utf-8"))
    print(df)
