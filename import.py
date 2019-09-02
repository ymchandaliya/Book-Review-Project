import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine=create_engine("postgres://bftqfkexrtucxu:79677fd3c30aed91117949656c9b2aa42663fb3ef287ef94a4f862738370c1cd@ec2-174-129-27-158.compute-1.amazonaws.com:5432/dch7g1rbas0o3o")
db=scoped_session(sessionmaker(bind=engine))

def main():
    fh=open("books.csv")
    reader=csv.reader(fh)
    for isbn,title,author,year in reader:
        db.execute("insert into books(isbn,title,author,year) values (:isbn,:title,:author,:year)",{"isbn":isbn,"title":title,"author":author,"year":year})
    db.commit()

if __name__ == '__main__':
    main()
