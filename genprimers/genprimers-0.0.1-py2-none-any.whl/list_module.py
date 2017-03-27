from Bio import SeqIO


def list_sequences(fasta_file):
    for record in SeqIO.parse(fasta_file, "fasta"):
        print(record.id+"\t"+record.description)
