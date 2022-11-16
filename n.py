import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response
import datetime, time

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)



DB_USER = "cy2620"
DB_PASSWORD = "6142"
DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"
DATABASEURI = "postgresql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_SERVER+"/proj1part2"


engine = create_engine(DATABASEURI)
# Here we create a test table and insert some values in it


engine.execute("""DROP TABLE IF EXISTS test;""")
engine.execute("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);""")
engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")

engine.execute("""INSERT INTO test VALUES (10, 'NEW grace hopper');""")


@app.before_request
def before_request():
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  try:
    g.conn.close()
  except Exception as e:
    pass

@app.route('/')
def index():

  #
  # example of a database query
  #
  cursor = g.conn.execute("SELECT * FROM Users")
  names = []
  for result in cursor:
    names.append(result)  # can also be accessed using result[0]
  cursor.close()

#Passing data
  context = dict(data = names)
# render_template looks in the templates/ folder for files.
  return render_template("index.html", **context)

@app.route('/card')
def card():
  cursor = g.conn.execute("SELECT * FROM Cards")
  names_card = []
  for result in cursor:
    names_card.append(result)
  cursor.close()
  context = dict(data_card = names_card)
  return render_template("card.html", **context)

@app.route('/deck')
def deck():
  deckid_mat=[]
  cursor = g.conn.execute("SELECT * FROM Decks")
  deck_table = []
  for result in cursor:
    deck_table.append(result)
  cursor.close()
  names_deck = [x[0] for x in deck_table]
  deckid_mat.append(deck_table)
  deckid_mat.append(range(len(names_deck)))
  context = dict(data_deck = deckid_mat)

  decklist_mat=[[],[],[]]
  for e in names_deck:
    cmd = 'SELECT DISTINCT user_id, card_id FROM Publishes_Contains WHERE deck_id= (:deckname)';
    cursor_pdl = g.conn.execute(text(cmd), deckname = e);
    card_in_deck = []
    for result in cursor_pdl:
      card_in_deck.append(result)
    cursor_pdl.close()  
    decklist_mat[0].append(e) #deck name
    decklist_mat[1].append(card_in_deck) #main table
    
  for i in range(len(decklist_mat[1])): #ith deck
    authors = []
    for j in decklist_mat[1][i]: #jth (uploader, card name) tuple
      authors.append(j[0])
    decklist_mat[2].append(set(authors))
  context2 = dict(data_deck2 = decklist_mat)

  comment_mat=[[],[]]
  for e in names_deck:
    cmd = 'SELECT user_id, comment_made_date, comment_content FROM Makes_Comments WHERE deck_id= (:deckname)';
    cursor_cm = g.conn.execute(text(cmd), deckname = e);
    comments = []
    for result in cursor_cm:
      comments.append(result)
    cursor_cm.close()  
    comment_mat[0].append(e) #deck name
    comment_mat[1].append(comments) #main table
  context3 = dict(data_deck3 = comment_mat)

  cursor = g.conn.execute("SELECT * FROM Cards")
  names_card = []
  for result in cursor:
    names_card.append(result)
  cursor.close()
  context4 = dict(data_card = names_card)

  return render_template("deck.html", **context, **context2, **context3, **context4)




# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
  name = int(request.form['name'])
  em = str(request.form['em'])
  cmd = 'INSERT INTO Users VALUES (:name1,:em)';
  g.conn.execute(text(cmd), name1 = name,em=em);
  return redirect('/')


def iso(time, time_format="%Y-%m-%d %H:%M:%S"):
    return time.strftime(time_format)

@app.route('/addcmt', methods=['POST'])
def addcmt():
  username_cmt = int(request.form['username_cmt'])
  deckname_cmt = int(request.form['deckname_cmt'])
  cmt_content = str(request.form['cmt_content'])
  cmd = 'INSERT INTO Makes_Comments VALUES (:username_cmt, :deckname_cmt, :timestamp_now,:cmt_content)';
  g.conn.execute(text(cmd), username_cmt = username_cmt, deckname_cmt=deckname_cmt, timestamp_now=iso(datetime.datetime.now()), cmt_content=cmt_content);
  return redirect('/')


@app.route('/addcard', methods=['POST'])
def addcard():
  cardname_add = str(request.form['cardname_add'])
  cardprice_add = float(request.form['cardprice_add'])
  cmd = 'INSERT INTO Cards VALUES (:cardname_add, :cardprice_add)';
  g.conn.execute(text(cmd), cardname_add = cardname_add, cardprice_add=cardprice_add);
  return redirect('/')

@app.route('/adddeck', methods=['POST'])
def adddeck():
  deckname_add = str(request.form['deckname_add'])
  cmd = 'INSERT INTO Decks VALUES (:deckname_add, :timestamp_now)';
  g.conn.execute(text(cmd), deckname_add = deckname_add, timestamp_now=iso(datetime.datetime.now()));
  return redirect('/')

@app.route('/addcard2deck', methods=['POST'])
def addcard2deck():
  username_addcd = str(request.form['username_addcd'])
  deckname_addcd = str(request.form['deckname_addcd'])
  cardname_addcd = str(request.form['cardname_addcd'])
  cmd = 'INSERT INTO Publishes_Contains VALUES (:username_addcd, :deckname_addcd, :cardname_addcd)';
  g.conn.execute(text(cmd), username_addcd=username_addcd, deckname_addcd=deckname_addcd, cardname_addcd=cardname_addcd);
  return redirect('/')

@app.route('/process-number', methods=['GET', 'POST'])
def process_number():
    if request.method == 'POST':
        selected_number = request.form['number']
        # do what you want
    return redirect('/')


@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()

