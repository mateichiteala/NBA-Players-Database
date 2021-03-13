import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter.ttk import Combobox
from ttkthemes import ThemedStyle
import cx_Oracle


def add_player(l_name, f_name, salary, status, id_echipa):
    id_team = (id_echipa.get()[0] + id_echipa.get()[1]).rstrip()
    c = conn.cursor()
    c.execute("SELECT buget FROM Echipe WHERE id_echipa=" + id_team)
    print("" + id_echipa.get()[1])
    row = c.fetchall()
    status_bool = 0
    if status.get() == 'Indisponibil':
        status_bool = 0
    else:
        status_bool = 1
    if id_team == '0':
        c.execute("INSERT INTO Jucatori (nume, prenume, salariu, status, id_echipa) VALUES (:l_name, :f_name, :salary, "
                  ":status, :id_echipa)",
                  {
                      'l_name': l_name.get(),
                      'f_name': f_name.get(),
                      'salary': salary.get(),
                      'status': status_bool,
                      'id_echipa': id_team
                  })
        c.execute("UPDATE Echipe SET "
                  "nr_jucatori = nr_jucatori + 1"
                  + " WHERE id_echipa = 0")
        conn.commit()
        messagebox.showinfo("Adaugare Jucator", "Jucatorul " + l_name.get() + " " + f_name.get() + "a fost adaugat in "
                                                                                                   "FARA ECHIPA")

    elif row[0][0] > int(salary.get()):
        c.execute("INSERT INTO Jucatori (nume, prenume, salariu, status, id_echipa) VALUES (:l_name, :f_name, :salary, "
                  ":status, :id_echipa)",
                  {
                      'l_name': l_name.get(),
                      'f_name': f_name.get(),
                      'salary': salary.get(),
                      'status': status_bool,
                      'id_echipa': id_team
                  })
        c.execute("UPDATE Echipe SET "
                  "nr_jucatori = nr_jucatori + 1, "
                  "buget = buget - " + salary.get() + " WHERE id_echipa = " + id_team)
        conn.commit()
        messagebox.showinfo("Adaugare Jucator", "Jucatorul " + l_name.get() + " " + f_name.get() + "a fost adaugat in "
                                                                                                   "echipa: "
                            + id_echipa.get()[3:(len(id_echipa.get()) - 1)])
        print("INSERT PLAYER " + l_name.get() + " " + f_name.get())
    else:
        messagebox.showinfo("Eroare", "Salariul jucatorului este prea mare pentru echipa cu id:" +
                            id_echipa.get()[3:(len(id_echipa.get()) - 1)])


def delete_player(id_player_raw):
    c = conn.cursor()

    id_player = (id_player_raw.get()[0] + id_player_raw.get()[1]).rstrip()
    # stergere detalii
    delete_details(id_player)

    # stergere Istorie
    c.execute("DELETE FROM Istorie WHERE id_jucator = " + id_player)
    # conn.commit()
    print("DELETE HISTORY FOR PLAYER: " + id_player)

    # scade nr de jucatori din echipa playerului
    c.execute("UPDATE Echipe SET nr_jucatori=nr_jucatori - 1, buget = buget + (SELECT salariu FROM Jucatori WHERE "
              "id_jucator =" + id_player + ") WHERE id_echipa = (SELECT id_echipa FROM Jucatori where "
                                           "id_jucator = " + id_player + ")")
    # afisare messagebox
    c.execute("SELECT nume, prenume FROM Jucatori WHERE id_jucator = " + id_player)
    row = c.fetchall()
    messagebox.showinfo("Stergere", "Jucatorul " + row[0][0] + " " + row[0][1] + " a fost sters")

    # delete din jucatori
    c.execute("DELETE FROM Jucatori WHERE id_jucator = " + id_player)

    conn.commit()

    print("DELETE PLAYER: " + id_player)


def modify_player(l_name, f_name, salary, status_raw, id_jucator_raw):
    id_jucator = (id_jucator_raw.get()[0] + id_jucator_raw.get()[1]).strip()
    c = conn.cursor()
    str_l_name = ""
    str_f_name = ""
    str_salary = ""
    str_status = ""
    str_id_echipa = ""
    ok = 0
    if status_raw.get() == 'Indisponibil':
        status = '1'
    else:
        status = '0'

    if l_name.get():
        str_l_name = " nume='" + l_name.get() + "', "
        ok = 1
    if f_name.get():
        str_f_name = " prenume='" + f_name.get() + "', "
        ok = 2
    if salary.get():
        str_salary = " salariu=" + salary.get() + ", "
        ok = 3
    if status_raw.get():
        str_status = " status=" + status + ", "
        ok = 4
    # if id_echipa.get():
    #    str_id_echipa = " id_echipa=" + id_echipa.get() + ", "
    #    ok = 5

    if ok == 1:
        str_l_name = str_l_name[:len(str_l_name) - 2]
    if ok == 2:
        str_f_name = str_f_name[:len(str_f_name) - 2]
    if ok == 3:
        str_salary = str_salary[:len(str_salary) - 2]
    if ok == 4:
        str_status = str_status[:len(str_status) - 2]
    # if ok == 5:
    #  str_id_echipa = str_id_echipa[:len(str_id_echipa) - 2]
    c.execute("SELECT buget FROM echipe WHERE id_echipa=(SELECT id_echipa FROM Jucatori WHERE id_jucator=" + str(
        id_jucator) + ")")
    buget_initial = c.fetchall()

    if str_salary != "":
        c.execute("SELECT salariu FROM Jucatori WHERE id_jucator = " + str(id_jucator))
        salariu_initial = c.fetchall()
        dif = int(salary.get()) - salariu_initial[0][0]
        if dif <= buget_initial[0][0]:
            c.execute(
                "UPDATE Echipe SET buget = buget - " + str(dif) + "WHERE id_echipa=(SELECT id_echipa FROM Jucatori "
                                                                  "WHERE "
                                                                  "id_jucator=" + str(
                    id_jucator) + ")")
            sequence = """UPDATE Jucatori SET """ + str_l_name + str_f_name + str_salary + str_status + str_id_echipa \
                       + " WHERE id_jucator=" + str(id_jucator)
            c.execute(sequence)
            conn.commit()
            messagebox.showinfo("Modificare", "Jucatorul a fost modificat.")
            print("MODIFY PLAYER " + l_name.get() + " " + f_name.get())
        else:
            messagebox.showinfo("ERR-MODIFICARE", "SALARIUL JUCATORULUI ESTE PREA MARE.")
    else:
        sequence = """UPDATE Jucatori SET """ + str_l_name + str_f_name + str_status \
                   + " WHERE id_jucator=" + str(id_jucator)
        c.execute(sequence)
        conn.commit()
        messagebox.showinfo("Modificare", "Jucatorul a fost modificat.")
        print("MODIFY PLAYER " + l_name.get() + " " + f_name.get())


def addPressed_player():
    import re
    player = tk.Tk()

    player.title("Jucatori")
    player.geometry("250x200")

    # Creeare chenare
    tk.Label(player, text="Nume").grid(row=0)
    tk.Label(player, text="Prenume").grid(row=1)
    tk.Label(player, text="Salariu").grid(row=2)
    # status = daca e valabil de vanzare sau nu
    tk.Label(player, text="Status").grid(row=3)
    tk.Label(player, text="ID Echipa").grid(row=4)

    l_name = tk.Entry(player)
    f_name = tk.Entry(player)
    salary = tk.Entry(player)
    status = tk.Entry(player)
    # id_team = tk.Entry(add)

    l_name.grid(row=0, column=1)
    f_name.grid(row=1, column=1)
    salary.grid(row=2, column=1)
    status.grid(row=3, column=1)
    # id_team.grid(row=4, column=1)

    # Choice Box for id teams
    c = conn.cursor()
    sequence = """ SELECT id_echipa, nume_echipa FROM Echipe"""
    c.execute(sequence)
    row = c.fetchall()
    # for i in row:
    #     i[1] = re.split("{", "", i[1])
    variable = StringVar(root)
    variable.set('1')
    id_team = Combobox(player, values=row)
    id_team.grid(row=4, column=1)

    # Choice Box for status
    c = conn.cursor()
    #  sequence = """ SELECT id_echipa FROM Echipe"""
    # c.execute(sequence)
    row = ["Indisponibil", "Valabil"]
    variable = StringVar(root)
    variable.set('1')
    status = Combobox(player, values=row)
    status.grid(row=3, column=1)

    insert_button = Button(player, text="Adauga Jucator",
                           command=lambda: add_player(l_name, f_name, salary, status, id_team))
    insert_button.place(x=50, y=130)


def deletePressed_player():
    player = tk.Tk()

    player.title("Jucatori-STERGERE")
    player.geometry("250x80")

    # Creeare chenare
    tk.Label(player, text="ID Jucator").grid(row=0)
    # id_jucator = tk.Entry(add)
    # id_jucator.grid(row=0, column=1)

    # Choice Box for id teams
    c = conn.cursor()
    sequence = """ SELECT id_jucator, nume, prenume FROM Jucatori"""
    c.execute(sequence)
    row = c.fetchall()
    variable = StringVar(root)
    variable.set('1')
    id_player = Combobox(player, values=row)
    id_player.grid(row=0, column=1)

    delete_button = Button(player, text="Sterge Jucator",
                           command=lambda: delete_player(id_player))
    delete_button.place(x=40, y=30)


"""
def modifyPressed_player():
    player = tk.Tk()

    player.title("Jucatori-MODIFICARE")
    player.geometry("250x200")

    # Creeare chenare
    tk.Label(player, text="ID Jucator").grid(row=1)
    tk.Label(player, text="Nume").grid(row=2)
    tk.Label(player, text="Prenume").grid(row=3)
    tk.Label(player, text="Salariu").grid(row=4)
    # status = daca e valabil de vanzare sau nu
    tk.Label(player, text="Status").grid(row=5)

    l_name = tk.Entry(player)
    f_name = tk.Entry(player)
    salary = tk.Entry(player)
    status = tk.Entry(player)

    # d_jucator = tk.Entry(player)

    # id_jucator.grid(row=1, column=1)
    l_name.grid(row=2, column=1)
    f_name.grid(row=3, column=1)
    salary.grid(row=4, column=1)
    status.grid(row=5, column=1)

    c = conn.cursor()
    sequence = """ 'SELECT id_jucator FROM Jucatori'"""
    c.execute(sequence)
    row = c.fetchall()
    variable = StringVar(root)
    variable.set('1')
    id_jucator = Combobox(player, values=row)
    id_jucator.grid(row=1, column=1)

    row2 = [0, 1]
    variable = StringVar(root)
    variable.set('1')
    status = Combobox(player, values=row2)
    status.grid(row=5, column=1)

    modify_button = Button(player, text="Modifica Jucator",
                           command=lambda: modify_player(l_name, f_name, salary, status, id_jucator))
    modify_button.place(x=50, y=130)

"""


def modifyPressed_player():
    player = tk.Tk()

    player.title("Jucatori-MODIFICARE")
    player.geometry("250x200")

    # Creeare chenare
    tk.Label(player, text="Alege Jucator").grid(row=0)

    tk.Label(player, text="Nume").grid(row=2)
    tk.Label(player, text="Prenume").grid(row=3)
    tk.Label(player, text="Salariu").grid(row=4)
    # status = daca e valabil de vanzare sau nu
    tk.Label(player, text="Status").grid(row=5)

    l_name = tk.Entry(player)
    f_name = tk.Entry(player)
    salary = tk.Entry(player)
    status = tk.Entry(player)

    # d_jucator = tk.Entry(player)

    # id_jucator.grid(row=1, column=1)
    l_name.grid(row=2, column=1)
    f_name.grid(row=3, column=1)
    salary.grid(row=4, column=1)
    status.grid(row=5, column=1)

    c = conn.cursor()
    sequence = """ SELECT id_jucator, nume, prenume FROM Jucatori"""
    c.execute(sequence)
    row = c.fetchall()
    variable = StringVar(root)
    variable.set('1')
    id_jucator = Combobox(player, values=row)
    id_jucator.grid(row=0, column=1)

    row2 = ['Indisponibil', 'Valabil']
    variable = StringVar(root)
    variable.set('1')
    status = Combobox(player, values=row2)
    status.grid(row=5, column=1)

    choose_player = Button(player, text="Alege Jucator",
                           command=lambda: setText(id_jucator, l_name, f_name, salary, status)).grid(row=1)

    modify_button = Button(player, text="Modifica Jucator",
                           command=lambda: modify_player(l_name, f_name, salary, status, id_jucator))
    modify_button.place(x=50, y=150)


def setText(id_jucator, l_name, f_name, salary, status):
    entries = [l_name, f_name, salary, status]
    for e in entries:
        e.delete(0, "end")

    c = conn.cursor()
    c.execute("SELECT nume, prenume, salariu, status FROM Jucatori WHERE id_jucator = " + (
            id_jucator.get()[0] + id_jucator.get()[1]).strip())

    row = c.fetchall()

    l_name.insert(0, str(row[0][0]))
    f_name.insert(0, str(row[0][1]))
    salary.insert(0, str(row[0][2]))
    if (str(row[0][3])) == '1':
        status.insert(0, 'Indisponibil')
    else:
        status.insert(0, 'Valabil')


def visualizePressed_player():
    visualize = tk.Tk()

    visualize.title("Jucatori - Vizualizare")
    # visualize.geometry("600x500")

    tree = ttk.Treeview(visualize, column=("c1", "c2", "c3", "c4", "c5", "c6"), show='headings')

    tree.column("#1", anchor=tk.CENTER)
    tree.heading("#1", text="id_jucator")

    tree.column("#2", anchor=tk.CENTER)
    tree.heading("#2", text="Echipa")

    tree.column("#3", anchor=tk.CENTER)
    tree.heading("#3", text="Prenume")

    tree.column("#4", anchor=tk.CENTER)
    tree.heading("#4", text="Nume")

    tree.column("#5", anchor=tk.CENTER)
    tree.heading("#5", text="Salariu")

    tree.column("#6", anchor=tk.CENTER)
    tree.heading("#6", text="Status")

    tree.pack()

    c = conn.cursor()
    sequence = """SELECT id_jucator, e.nume_echipa, prenume, nume, salariu, status
                    FROM Jucatori j, Echipe e 
                    WHERE e.id_echipa = j.id_echipa ORDER BY j.id_jucator ASC"""
    c.execute(sequence)
    records = c.fetchall()
    for e, i in enumerate(records):
        itemlist = list(i)
        if itemlist[-1] == '0':
            itemlist[-1] = 'Valabil'
        else:
            itemlist[-1] = 'Indisponibl'
        i = tuple(itemlist)
        records[e] = i

    for row in records:
        tree.insert("", tk.END, values=row)


#######################

def add_team(t_name, location, budget):
    c = conn.cursor()
    if location.get():
        c.execute("INSERT INTO Echipe (nume_echipa, buget, nr_jucatori, locatia) VALUES (:t_name, :budget, 0, "
                  ":location)",
                  {
                      't_name': t_name.get(),
                      'budget': budget.get(),
                      # 'nr_players': nr_players.get(),
                      'location': location.get(),
                  })
    else:
        c.execute("INSERT INTO Echipe (nume_echipa, buget, nr_jucatori) VALUES (:t_name, :budget, 0)",
                  {
                      't_name': t_name.get(),
                      'budget': budget.get(),
                      # 'nr_players': nr_players.get(),
                  })
    conn.commit()
    messagebox.showinfo("ECHIPA", "ECHIPA ADAUGATA:" + t_name.get())
    print("INSERT TEAM " + t_name.get())


def addPressed_team():
    team = tk.Tk()

    team.title("Echipe")
    team.geometry("250x100")

    # Creeare chenare
    tk.Label(team, text="Nume Echipa").grid(row=0)
    tk.Label(team, text="Buget").grid(row=1)
    # tk.Label(team, text="Numar jucatori").grid(row=2)
    tk.Label(team, text="Locatia").grid(row=3)

    t_name = tk.Entry(team)
    buget = tk.Entry(team)
    #  nr_players = tk.Entry(team)
    location = tk.Entry(team)

    t_name.grid(row=0, column=1)
    buget.grid(row=1, column=1)
    # nr_players.grid(row=2, column=1)
    location.grid(row=3, column=1)

    insert_button = Button(team, text="Adauga Echipa",
                           command=lambda: add_team(t_name, location, buget))
    insert_button.place(x=60, y=70)


def delete_team(id_team_raw):
    c = conn.cursor()
    id_team = (id_team_raw.get()[0] + id_team_raw.get()[1]).strip()
    sequnece = ("DELETE FROM ISTORIE  WHERE id_echipa=" + id_team)
    c.execute(sequnece)
    print("DELETE ID HISTORY WHERE ID TEAM: " + id_team)
    conn.commit()

    sequence = ("UPDATE Jucatori SET id_echipa = 0, status = 0"
                " WHERE id_echipa=" + id_team)
    c.execute(sequence)
    print("MODIFY PLAYERS WITH ID_TEAM:" + id_team + " TO ID_TEAM: 0")
    conn.commit()

    c.execute(
        "UPDATE Echipe SET nr_jucatori = (SELECT COUNT(id_jucator) FROM Jucatori WHERE id_echipa = 0) WHERE id_echipa = 0")
    conn.commit()

    c.execute("DELETE FROM Echipe WHERE id_echipa = " + id_team)
    print("DELETE TEAM WITH ID : " + id_team)
    conn.commit()
    messagebox.showinfo("STERGERE",
                        "ECHIPA:" + id_team_raw.get()[3:(len(id_team_raw.get()) - 1)].strip("{") + " STEARSA")


def deletePressed_team():
    team = tk.Tk()

    team.title("ECHIPA-STERGERE")
    team.geometry("250x70")

    # Creeare chenare
    tk.Label(team, text="ID Echipa").grid(row=0)
    # id_team = tk.Entry(team)
    # id_team.grid(row=0, column=1)

    # Choice Box for id teams
    c = conn.cursor()
    sequence = """ SELECT id_echipa, nume_echipa FROM Echipe WHERE id_echipa != 0"""
    c.execute(sequence)
    row = c.fetchall()
    variable = StringVar(root)
    variable.set('1')
    id_team = Combobox(team, values=row)
    id_team.grid(row=0, column=1)

    delete_button = Button(team, text="Sterge Echipa",
                           command=lambda: delete_team(id_team))
    delete_button.place(x=50, y=35)


def modify_team(t_name, budget, location, id_team_raw):
    id_team = (id_team_raw.get()[0] + id_team_raw.get()[1]).strip()
    c = conn.cursor()
    str_t_name = ""
    str_budget = ""
    # str_nr_players = ""
    str_location = ""

    ok = 0
    if t_name.get():
        str_t_name = " nume_echipa='" + t_name.get() + "', "
        ok = 1
    if budget.get():
        str_budget = " buget=" + budget.get() + ", "
        ok = 2
    # if nr_players.get():
    #    str_nr_players = " nr_jucatori=" + nr_players.get() + ", "
    #    ok = 3
    if location.get():
        str_location = " locatia='" + location.get() + "', "
        ok = 4

    if ok == 1:
        str_t_name = str_t_name[:len(str_t_name) - 2]
    if ok == 2:
        str_budget = str_budget[:len(str_budget) - 2]
    # if ok == 3:
    #     str_nr_players = str_nr_players[:len(str_nr_players) - 2]
    if ok == 4:
        str_location = str_location[:len(str_location) - 2]

    # if str_budget != "":
    # c.execute("SELECT sum(salariu) FROM jucatori WHERE id_echipa = " + id_team)
    # salary_sum = c.fetchall()
    # if int(budget.get()) + int(salary_sum[0][0]) <= 100:
    sequence = ("UPDATE Echipe SET " + str_t_name + str_budget
                + str_location +
                " WHERE id_echipa=" + id_team)
    c.execute(sequence)
    conn.commit()
    print("MODIFY TEAM " + t_name.get())
    messagebox.showinfo("MODIFICARE-ECHIPA",
                        "ECHIPA MODIFICATA:" + id_team_raw.get()[2:(len(id_team_raw.get()) - 1)].strip("{"))

    # else: else: sequence = ("UPDATE Echipe SET " + str_t_name + str_budget + str_location + " WHERE id_echipa=" +
    # id_team) c.execute(sequence) conn.commit() print("MODIFY TEAM " + t_name.get()) messagebox.showinfo(
    # "MODIFICARE-ECHIPA", "ECHIPA MODIFICATA:" + id_team_raw.get()[2:(len(id_team_raw.get())-1)].strip("{"))


def setText_team(id_team, t_name, buget, location):
    entries = [t_name, buget, location]
    for e in entries:
        e.delete(0, "end")

    c = conn.cursor()
    c.execute("SELECT nume_echipa, buget, locatia FROM Echipe WHERE id_echipa = " + (
            id_team.get()[0] + id_team.get()[1]).strip())

    row = c.fetchall()

    t_name.insert(0, row[0][0])
    buget.insert(0, row[0][1])
    if row[0][2] is not None:
        location.insert(0, row[0][2])


def modifyPressed_team():
    team = tk.Tk()

    team.title("Echipe")
    team.geometry("250x230")

    # Creeare chenare
    tk.Label(team, text="ID Echipa").grid(row=0)
    tk.Label(team, text="Nume Echipa").grid(row=2)
    tk.Label(team, text="Buget").grid(row=3)
    # tk.Label(team, text="Numar jucatori").grid(row=3)
    tk.Label(team, text="Locatia").grid(row=4)

    t_name = tk.Entry(team)
    buget = tk.Entry(team)
    # nr_players = tk.Entry(team)
    location = tk.Entry(team)
    id_team = tk.Entry(team)

    t_name.grid(row=2, column=1)
    buget.grid(row=3, column=1)
    # nr_players.grid(row=2, column=1)
    location.grid(row=4, column=1)
    # id_team.grid(row=0, column=1)

    # Choice Box for id teams
    c = conn.cursor()
    sequence = """ SELECT id_echipa, nume_echipa FROM Echipe WHERE id_echipa != 0"""
    c.execute(sequence)
    row = c.fetchall()
    variable = StringVar(root)
    variable.set('1')
    id_team = Combobox(team, values=row)
    id_team.grid(row=0, column=1)

    choose_team = Button(team, text="Alege Echipa",
                         command=lambda: setText_team(id_team, t_name, buget, location)).grid(row=1)
    modify_button = Button(team, text="Modifica Echipa",
                           command=lambda: modify_team(t_name, buget, location, id_team))
    modify_button.place(x=50, y=130)


def visualizePressed_team():
    visualize = tk.Tk()

    visualize.title("Echipe - Vizualizare")
    # visualize.geometry("600x500")

    tree = ttk.Treeview(visualize, column=("c1", "c2", "c3", "c4", "c5"), show='headings')

    tree.column("#1", anchor=tk.CENTER)
    tree.heading("#1", text="id_echipa")

    tree.column("#2", anchor=tk.CENTER)
    tree.heading("#2", text="Nume Echipa")

    tree.column("#3", anchor=tk.CENTER)
    tree.heading("#3", text="Buget")

    tree.column("#4", anchor=tk.CENTER)
    tree.heading("#4", text="Numar Jucatori")

    tree.column("#5", anchor=tk.CENTER)
    tree.heading("#5", text="Locatie")

    tree.pack()

    c = conn.cursor()
    sequence = """ SELECT * FROM Echipe"""
    c.execute(sequence)
    records = c.fetchall()

    for row in records:
        tree.insert("", tk.END, values=row)


########################

def add_details(cnp, birthday, country, email, phone_number, id_player_raw):
    id_player = (id_player_raw.get()[0] + id_player_raw.get()[1]).rstrip()
    c = conn.cursor()
    ok_e = 0
    ok_p = 0
    if email.get():
        ok_e = 1
    if phone_number.get():
        ok_p = 1

    if ok_e == 1 and ok_p == 1:
        c.execute("INSERT INTO Detalii_Jucatori (cnp, id_jucator, data_nasterii, tara, email, telefon ) "
                  "VALUES (:cnp, :id_player, :birthday, :country, :email, :phone_number )",
                  {
                      'cnp': cnp.get(),
                      'id_player': id_player,
                      'birthday': birthday.get(),
                      'country': country.get(),
                      'email': email.get(),
                      'phone_number': phone_number.get()
                  })
    if ok_e == 1 and ok_p == 0:
        c.execute("INSERT INTO Detalii_Jucatori (cnp, id_jucator, data_nasterii, tara, email) "
                  "VALUES (:cnp, :id_player, :birthday, :country, :email)",
                  {
                      'cnp': cnp.get(),
                      'id_player': id_player,
                      'birthday': birthday.get(),
                      'country': country.get(),
                      'email': email.get(),
                  })
    if ok_e == 0 and ok_p == 1:
        c.execute("INSERT INTO Detalii_Jucatori (cnp, id_jucator, data_nasterii, tara, telefon) "
                  "VALUES (:cnp, :id_player, :birthday, :country, :phone_number)",
                  {
                      'cnp': cnp.get(),
                      'id_player': id_player,
                      'birthday': birthday.get(),
                      'country': country.get(),
                      'phone_number': phone_number.get(),
                  })
    if ok_e == 0 and ok_p == 0:
        c.execute("INSERT INTO Detalii_Jucatori (cnp, id_jucator, data_nasterii, tara) "
                  "VALUES (:cnp, :id_player, :birthday, :country)",
                  {
                      'cnp': cnp.get(),
                      'id_player': id_player,
                      'birthday': birthday.get(),
                      'country': country.get(),
                  })

    conn.commit()
    print("INSERT DETAILS FOR PLAYER " + id_player)


def addPressed_details():
    details = tk.Tk()

    details.title("Detalii Jucatori")
    details.geometry("250x200")

    # Creeare chenare
    tk.Label(details, text="ID Player").grid(row=0)
    tk.Label(details, text="CNP").grid(row=1)
    tk.Label(details, text="Data Nasterii").grid(row=2)
    tk.Label(details, text="Tara").grid(row=3)
    tk.Label(details, text="Email").grid(row=4)
    tk.Label(details, text="Telefon").grid(row=5)

    cnp = tk.Entry(details)
    birthday = tk.Entry(details)
    country = tk.Entry(details)
    email = tk.Entry(details)
    phone_number = tk.Entry(details)

    cnp.grid(row=1, column=1)
    birthday.grid(row=2, column=1)
    country.grid(row=3, column=1)
    email.grid(row=4, column=1)
    phone_number.grid(row=5, column=1)

    # Choice Box for id players
    c = conn.cursor()
    sequence = """ SELECT id_jucator, nume, prenume FROM Jucatori"""
    c.execute(sequence)
    row = c.fetchall()
    variable = StringVar(root)
    variable.set('1')
    id_player = Combobox(details, values=row)
    id_player.grid(row=0, column=1)

    insert_button = Button(details, text="Adauga Detalii Jucatori",
                           command=lambda: add_details(cnp, birthday, country, email, phone_number, id_player))
    insert_button.place(x=50, y=130)


def delete_details(id_player):
    c = conn.cursor()
    c.execute("DELETE FROM Detalii_Jucatori WHERE id_jucator = " + id_player)
    conn.commit()
    print("DELETE DETAILS FOR PLAYER " + id_player)


def delete_details2(id_player):
    c = conn.cursor()
    c.execute("DELETE FROM Detalii_Jucatori WHERE id_jucator = " + (id_player.get()[0] + id_player.get()[1].rstrip()))
    conn.commit()
    messagebox.showinfo("Stergere Detalii",
                        "Au fost sterse detaliile pentru: " + id_player.get()[3:(len(id_player.get()) - 1)].strip("{"))
    # print("DELETE DETAILS FOR PLAYER " + id_player)


def deletePressed_details():
    details = tk.Tk()

    details.title("Detalii-STERGERE")
    details.geometry("250x70")

    tk.Label(details, text="ID Jucator").grid(row=0)

    # Choice Box for id players
    c = conn.cursor()
    sequence = """ SELECT id_jucator, nume, prenume FROM Jucatori"""
    c.execute(sequence)
    row = c.fetchall()
    variable = StringVar(root)
    variable.set('1')
    id_player = Combobox(details, values=row)
    id_player.grid(row=0, column=1)

    delete_button = Button(details, text="Sterge Detalii Jucatori",
                           command=lambda: delete_details2(id_player))
    delete_button.place(x=50, y=35)


def modify_details(cnp, birthday, country, email, phone_number, id_player_raw):
    id_player = (id_player_raw.get()[0] + id_player_raw.get()[1]).rstrip()
    c = conn.cursor()
    str_cnp = ""
    str_birthday = ""
    str_country = ""
    str_email = ""
    str_phone_number = ""

    ok = 0
    if cnp.get():
        str_cnp = " cnp='" + cnp.get() + "', "
        ok = 1
    if birthday.get():
        str_birthday = " data_nasterii=" + birthday.get() + ", "
        ok = 2
    if country.get():
        str_country = " tara='" + country.get() + "', "
        ok = 3
    if email.get():
        str_email = " email='" + email.get() + "', "
        ok = 4
    if phone_number.get():
        str_phone_number = " telefon='" + phone_number.get() + "', "
        ok = 5

    if ok == 1:
        str_cnp = str_cnp[:len(str_cnp) - 2]
    if ok == 2:
        str_birthday = str_birthday[:len(str_birthday) - 2]
    if ok == 3:
        str_country = str_country[:len(str_cnp) - 2]
    if ok == 4:
        str_email = str_email[:len(str_email) - 2]
    if ok == 5:
        str_phone_number = str_phone_number[:len(str_phone_number) - 2]

    sequence = ("UPDATE Detalii_Jucatori SET " + str_cnp + str_birthday
                + str_country + str_email + str_phone_number +
                " WHERE id_jucator=" + id_player)
    c.execute(sequence)
    conn.commit()
    messagebox.showinfo("Succes",
                        "Detalii Modificate " + id_player_raw.get()[2:len(id_player_raw.get()) - 1].strip("{"))


def modifyPressed_details():
    details = tk.Tk()

    details.title("Detalii-MODIFICARE")
    details.geometry("250x200")

    # Creeare chenare
    tk.Label(details, text="CNP").grid(row=0)
    tk.Label(details, text="Data Nasterii").grid(row=1)
    tk.Label(details, text="Tara").grid(row=2)
    tk.Label(details, text="Email").grid(row=3)
    tk.Label(details, text="Telefon").grid(row=4)
    tk.Label(details, text="ID Jucator").grid(row=5)

    cnp = tk.Entry(details)
    birthday = tk.Entry(details)
    country = tk.Entry(details)
    email = tk.Entry(details)
    phone_number = tk.Entry(details)

    cnp.grid(row=0, column=1)
    birthday.grid(row=1, column=1)
    country.grid(row=2, column=1)
    email.grid(row=3, column=1)
    phone_number.grid(row=4, column=1)

    # Choice Box for id players
    c = conn.cursor()
    sequence = """ SELECT id_jucator, nume, prenume FROM Jucatori"""
    c.execute(sequence)
    row = c.fetchall()
    variable = StringVar(root)
    variable.set('1')
    id_player = Combobox(details, values=row)
    id_player.grid(row=5, column=1)

    modify_button = Button(details, text="Modifica Detalii Jucatori",
                           command=lambda: modify_details(cnp, birthday, country, email, phone_number, id_player))
    modify_button.place(x=50, y=130)


def visualizePressed_details():
    visualize = tk.Tk()

    visualize.title("Echipe - Vizualizare")
    # visualize.geometry("600x500")

    tree = ttk.Treeview(visualize, column=("c1", "c2", "c3", "c4", "c5", "c6", "c7", "c8"), show='headings')

    tree.column("#1", anchor=tk.CENTER)
    tree.heading("#1", text="CNP")

    tree.column("#2", anchor=tk.CENTER)
    tree.heading("#2", text="id_jucator")

    tree.column("#3", anchor=tk.CENTER)
    tree.heading("#3", text="Nume")

    tree.column("#4", anchor=tk.CENTER)
    tree.heading("#4", text="Prenume")

    tree.column("#5", anchor=tk.CENTER)
    tree.heading("#5", text="Data Nasterii")

    tree.column("#6", anchor=tk.CENTER)
    tree.heading("#6", text="Tara")

    tree.column("#7", anchor=tk.CENTER)
    tree.heading("#7", text="Telefon")

    tree.column("#8", anchor=tk.CENTER)
    tree.heading("#8", text="Email")

    tree.pack()

    c = conn.cursor()
    sequence = """ SELECT d.cnp, d.id_jucator, j.nume, j.prenume, data_nasterii, tara, email, telefon  FROM Detalii_jucatori d, Jucatori j
                    WHERE d.id_jucator = j.id_jucator"""
    c.execute(sequence)
    records = c.fetchall()

    for row in records:
        tree.insert("", tk.END, values=row)


###########################
###########################

def add_history(id_player_raw, id_team_raw, nr_games, id_positions_raw, start_date_day, start_date_mon, start_date_year,
                end_date_day, end_date_mon, end_date_year):
    c = conn.cursor()

    id_player = (id_player_raw.get()[0] + id_player_raw.get()[1]).strip()
    id_team = (id_team_raw.get()[0] + id_team_raw.get()[1]).strip()
    id_positions = id_positions_raw.get()[0]

    games = nr_games.get()
    start = start_date_day.get() + "-" + start_date_mon.get() + "-" + start_date_year.get()
    end = end_date_day.get() + "-" + end_date_mon.get() + "-" + end_date_year.get()

    c.execute("INSERT INTO ISTORIE (id_jucator, id_echipa, nr_meciuri, id_pozitie, data_inceput, data_final) "
              "VALUES (:id_player, :id_team, :nr_games, :id_positions, :start_date, :end_date)",
              {
                  'id_player': id_player,
                  'id_team': id_team,
                  'nr_games': games,
                  'id_positions': id_positions,
                  'start_date': start,
                  'end_date': end
              })
    conn.commit()
    messagebox.showinfo("Succes", "Istorie inserata pentru jucatorul: " + str(
        id_player_raw.get()[2:len(id_player_raw.get())].strip("{")))
    print("INSERT HISTORY FOR PLAYER " + id_player)
    entries = [id_player_raw, id_team_raw, nr_games, id_positions_raw, start_date_day, start_date_mon, start_date_year,
               end_date_day, end_date_mon, end_date_year]

    for e in entries:
        e.delete(0, 'end')


def addPressed_history():
    history = tk.Tk()

    history.title("Istorie-Adaugare")
    history.geometry("380x270")

    # Creeare chenare
    tk.Label(history, text="Alege jucator").grid(row=0)
    tk.Label(history, text="Alege Echipa").grid(row=1)
    tk.Label(history, text="Numar meciuri").grid(row=2)
    tk.Label(history, text="Pozitie").grid(row=3)
    tk.Label(history, text="Data inceput").grid(row=4)
    tk.Label(history, text="Data final").place(x=10, y=130)

    nr_games = tk.Entry(history)
    # start_date = tk.Entry(history)
    # end_date = tk.Entry(history)

    mon = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
    days = list(range(1, 32))
    start_date_day = Combobox(history, values=days, width=4)
    start_date_mon = Combobox(history, values=mon, width=7)
    start_date_year = tk.Entry(history, width=10)

    end_date_day = Combobox(history, values=days, width=4)
    end_date_mon = Combobox(history, values=mon, width=7)
    end_date_year = tk.Entry(history, width=10)

    nr_games.grid(row=2, column=1)
    # start_date.grid(row=4, column=1)

    # end_date.grid(row=5, column=1)

    start_date_day.place(x=100, y=90)
    start_date_mon.place(x=160, y=90)
    start_date_year.place(x=250, y=90)

    end_date_day.place(x=100, y=130)
    end_date_mon.place(x=160, y=130)
    end_date_year.place(x=250, y=130)

    # Choice Box for id players
    c = conn.cursor()
    sequence = """ SELECT id_jucator, nume, prenume FROM Jucatori"""
    c.execute(sequence)
    row = c.fetchall()
    variable = StringVar(root)
    variable.set('1')
    id_player = Combobox(history, values=row)
    id_player.grid(row=0, column=1)

    # Choice Box for id teams
    c = conn.cursor()
    sequence = """ SELECT id_echipa, nume_echipa FROM Echipe"""
    c.execute(sequence)
    row = c.fetchall()
    variable = StringVar(root)
    variable.set('1')
    id_team = Combobox(history, values=row)
    id_team.grid(row=1, column=1)

    # Choice Box for id positions
    c = conn.cursor()
    sequence = """ SELECT id_pozitie, pozitie FROM Pozitii"""
    c.execute(sequence)
    row = c.fetchall()
    variable = StringVar(root)
    variable.set('1')
    id_positions = Combobox(history, values=row)
    id_positions.grid(row=3, column=1)

    insert_button = Button(history, text="Adauga Istorie",
                           command=lambda: add_history(id_player, id_team,
                                                       nr_games, id_positions, start_date_day, start_date_mon,
                                                       start_date_year, end_date_day, end_date_mon, end_date_year))
    insert_button.place(x=50, y=180)


def modify_or_deletePressed_history(switch):
    history = tk.Tk()

    history.title("Istorie-Adaugare")
    history.geometry("250x200")

    # Creeare chenare
    tk.Label(history, text="Selectare Jucator").grid(row=0)
    tk.Label(history, text="Data inceput").grid(row=1)
    tk.Label(history, text="Data final").grid(row=2)

    # Choice Box for id players
    c = conn.cursor()
    sequence = """ SELECT id_jucator, nume, prenume FROM Jucatori"""
    c.execute(sequence)
    row = c.fetchall()
    variable = StringVar(root)
    variable.set('1')
    id_player = Combobox(history, values=row)
    id_player.grid(row=0, column=1)

    set_button = Button(history, text="Seteaza Jucator",
                        command=lambda: setPressed_player(history, id_player, switch))
    set_button.place(x=10, y=200)


def setPressed_player(history, id_player_raw, switch):
    # Choice Box for start_date
    c = conn.cursor()
    id_player = (id_player_raw.get()[0] + id_player_raw.get()[1]).strip()

    sequence = """ SELECT data_inceput FROM Istorie WHERE id_jucator=""" + id_player

    c.execute(sequence)
    row = c.fetchall()

    variable = StringVar(root)
    variable.set('1')
    start_date = Combobox(history, values=row)
    start_date.grid(row=1, column=1)

    set_button_start = Button(history, text="Seteaza Data Inceput",
                              command=lambda: setPressed_date_start(history, id_player, start_date, switch))
    set_button_start.place(x=10, y=230)


def modify_history(id_player, start_date, end_date, start_date_new,
                   end_date_new, nr_games_new, id_positions, id_teams):
    c = conn.cursor()
    str_start_date_new = ""
    str_end_date_new = ""
    str_nr_games_new = ""
    str_id_positions = ""
    str_id_teams = ""

    ok = 0
    if start_date_new.get():
        str_start_date_new = " data_inceput=TO_DATE('" + start_date.get() + "', '{yyyy-mm-dd hh24:mi:ss}'), "
        ok = 1
    if end_date_new.get():
        str_end_date_new = " data_final=TO_DATE('" + start_date.get() + "', '{yyyy-mm-dd hh24:mi:ss}'), "
        ok = 2
    if nr_games_new.get():
        str_nr_games_new = " nr_meciuri='" + nr_games_new.get() + "', "
        ok = 3
    if id_positions.get():
        str_id_positions = " id_pozitie='" + id_positions.get() + "', "
        ok = 4
    if id_teams.get():
        str_id_teams = " id_echipa='" + id_teams.get() + "', "
        ok = 5

    if ok == 1:
        str_start_date_new = str_start_date_new[:len(str_start_date_new) - 2]
    if ok == 2:
        str_end_date_new = str_end_date_new[:len(str_end_date_new) - 2]
    if ok == 3:
        str_nr_games_new = str_nr_games_new[:len(str_nr_games_new) - 2]
    if ok == 4:
        str_id_positions = str_id_positions[:len(str_id_positions) - 2]
    if ok == 5:
        str_id_teams = str_id_teams[:len(str_id_teams) - 2]

    sequence = ("UPDATE ISTORIE SET " + str_start_date_new + str_end_date_new
                + str_nr_games_new + str_id_positions + str_id_teams +
                " WHERE (id_jucator=" + id_player +
                " AND data_inceput=TO_DATE('" + start_date.get() + "', '{yyyy-mm-dd hh24:mi:ss}')" +
                " AND data_final=TO_DATE('" + end_date.get() + "', '{yyyy-mm-dd hh24:mi:ss}'))")
    c.execute(sequence)
    conn.commit()
    messagebox.showinfo("Succes", "Istorie modificata pentru jucatorul cu ID = " + id_player)
    print("MODIFY HISTORY FOR PLAYER " + id_player)


def setPressed_date_start(history, id_player, start_date, switch):
    # Choice Box for end_date
    c = conn.cursor()

    sequence = """ SELECT data_final FROM Istorie 
                WHERE (id_jucator=""" + id_player + \
               "AND data_inceput= TO_DATE('" + start_date.get() + "', '{yyyy-mm-dd hh24:mi:ss}'))"
    c.execute(sequence)
    row = c.fetchall()
    variable = StringVar(root)
    variable.set('1')
    end_date = Combobox(history, values=row)
    end_date.grid(row=2, column=1)

    if switch == 1:
        # Creeare chenare
        tk.Label(history, text="DATA INCEPUT NOU").grid(row=4)
        tk.Label(history, text="Data FINAL NOU").grid(row=5)
        tk.Label(history, text="Numar Meciuri").grid(row=6)
        tk.Label(history, text="ID POZITIE").grid(row=7)
        tk.Label(history, text="ID Echipa").grid(row=8)

        start_date_new = tk.Entry(history)
        end_date_new = tk.Entry(history)
        nr_games_new = tk.Entry(history)

        start_date_new.grid(row=4, column=1)
        end_date_new.grid(row=5, column=1)
        nr_games_new.grid(row=6, column=1)

        # Choice Box for id positions
        c = conn.cursor()
        sequence = """ SELECT id_pozitie FROM Pozitii"""

        c.execute(sequence)
        row = c.fetchall()

        variable = StringVar(root)
        variable.set('1')
        id_positions = Combobox(history, values=row)
        id_positions.grid(row=7, column=1)

        # Choice Box for id teams
        c = conn.cursor()
        sequence = """ SELECT id_echipa FROM Echipe """

        c.execute(sequence)
        row = c.fetchall()

        variable = StringVar(root)
        variable.set('1')
        id_teams = Combobox(history, values=row)
        id_teams.grid(row=8, column=1)

        modify_button = Button(history, text="Modifica Istoric",
                               command=lambda: modify_history(id_player, start_date, end_date, start_date_new,
                                                              end_date_new,
                                                              nr_games_new, id_positions, id_teams))
        modify_button.place(x=10, y=260)
    else:
        del_button = Button(history, text="Sterger Istoric",
                            command=lambda: del_history(id_player, start_date, end_date))
        del_button.place(x=10, y=260)


def del_history(id_player, start_date, end_date):
    c = conn.cursor()
    c.execute("DELETE FROM Istorie WHERE (id_jucator=" + id_player +
              " AND data_inceput=TO_DATE('" + start_date.get() + "', '{yyyy-mm-dd hh24:mi:ss}')" +
              " AND data_final=TO_DATE('" + end_date.get() + "', '{yyyy-mm-dd hh24:mi:ss}'))")
    conn.commit()
    print("DELETE HISTORY FOR PLAYER " + id_player)


def visualizePressed_history():
    visualize = tk.Tk()

    visualize.title("Istorie - Vizualizare")
    # visualize.geometry("600x500")

    tree = ttk.Treeview(visualize, column=("c1", "c2", "c3", "c4", "c5", "c6", "c7", "c8"), show='headings')

    tree.column("#1", anchor=tk.CENTER)
    tree.heading("#1", text="id_istorie")

    tree.column("#2", anchor=tk.CENTER)
    tree.heading("#2", text="Prenume")

    tree.column("#3", anchor=tk.CENTER)
    tree.heading("#3", text="Nume")

    tree.column("#4", anchor=tk.CENTER)
    tree.heading("#4", text="Echipa")

    tree.column("#5", anchor=tk.CENTER)
    tree.heading("#5", text="Meciuri")

    tree.column("#6", anchor=tk.CENTER)
    tree.heading("#6", text="Pozitie")

    tree.column("#7", anchor=tk.CENTER)
    tree.heading("#7", text="data_inceput")

    tree.column("#8", anchor=tk.CENTER)
    tree.heading("#8", text="data_final")

    tree.pack()

    c = conn.cursor()
    sequence = """ SELECT id_istorie, j.prenume, j.nume, e.nume_echipa, nr_meciuri, p.pozitie, data_inceput, 
        data_final FROM Istorie i, Jucatori j, Echipe e, Pozitii p 
        WHERE  i.id_jucator = j.id_jucator AND i.id_echipa = e.id_echipa
        AND i.id_pozitie = p.id_pozitie ORDER BY i.id_istorie ASC"""
    c.execute(sequence)
    records = c.fetchall()

    for row in records:
        tree.insert("", tk.END, values=row)


def visualizePressed_positions():
    visualize = tk.Tk()

    visualize.title("Istorie - Vizualizare")
    # visualize.geometry("600x500")

    tree = ttk.Treeview(visualize, column=("c1", "c2"), show='headings')

    tree.column("#1", anchor=tk.CENTER)
    tree.heading("#1", text="id_pozitie")

    tree.column("#2", anchor=tk.CENTER)
    tree.heading("#2", text="Nume Pozitie")

    tree.pack()

    c = conn.cursor()
    sequence = """SELECT * FROM Pozitii"""
    c.execute(sequence)
    records = c.fetchall()

    for row in records:
        tree.insert("", tk.END, values=row)


def accept_function(switch, c, transaction_final):
    if switch == 1:
        conn.commit()
        messagebox.showinfo("Success", "Tranzactia a fost realizata")
    else:
        sequence = "ROLLBACK TO SAVEPOINT transfer"
        c.execute(sequence)
        messagebox.showinfo("Desclined", "Tranzactia a fost anulata")

    # inchidere fereastra de accept/decline
    transaction_final.destroy()


def transaction_function(id_echipa, transaction_player):
    id_player = (transaction_player.get()[0] + transaction_player.get()[1])
    c = conn.cursor()
    sequence = """ SELECT status FROM Jucatori WHERE id_jucator = """ + id_player
    c.execute(sequence)
    row = c.fetchall()
    # status = 0 => de vanzare

    #  sequence = """SELECT nr_jucatori FROM Echipe WHERE id_echipa = (SELECT id_echipa from Jucatori where id_jucator
    #  =""" + id_player + ") and id_echipa != 0"
    # c.execute(sequence)
    # nr_jucatori = c.fetchall()
    # print("Nr jucatori: " + str(nr_jucatori[0][0]))

    # verificare status
    if row[0][0] == "1":
        messagebox.showinfo("Transfer imposibil", "Jucatorul nu este de vanzare sau este in curs de trasfer")
        print("NU ESTE DE VANZARE/Este in curs de transfer")
    else:
        '''
        if int(nr_jucatori[0][0]) < 6:
            messagebox.showinfo("Transfer imposibil",
                                "Echipa jucatorului are doar " + str(nr_jucatori[0][0]) + "jucatori"
                                                                                          ". Nu se "
                                                                                          "poate "
                                                                                          "efectua "
                                                                                          "transferul)")
            print("Echipa jucatorului are doar " + str(nr_jucatori[0][0]) + ". Nu se poate efectua transferul.")
        else:
        '''
        sequence = """ SELECT buget FROM Echipe WHERE id_echipa = """ + id_echipa
        c.execute(sequence)
        row_budget = c.fetchall()

        sequence = """ SELECT salariu FROM Jucatori WHERE id_jucator = """ + id_player
        c.execute(sequence)
        row_salary = c.fetchall()

        salary = str(row_salary[0][0])

        if int(row_budget[0][0]) < int(row_salary[0][0]):
            messagebox.showinfo("Transfer imposibil", "Bugetul echipei este prea mic")
            print("BUGETUL PREA MIC")
        else:
            transaction_final = tk.Tk()

            transaction_final.title("Confirma Tranzactie")
            transaction_final.geometry("150x100")

            # Creeare chenare
            tk.Label(transaction_final, text="Confirma Transfer?").place(x=15, y=10)
            transaction_accept_button = Button(transaction_final, text="Confirm",
                                               command=lambda: accept_function(1, c, transaction_final))
            transaction_accept_button.place(x=10, y=30)

            transaction_decline_button = Button(transaction_final, text="Decline",
                                                command=lambda: accept_function(0, c, transaction_final))
            transaction_decline_button.place(x=80, y=30)
            # savepoint
            sequence = """SAVEPOINT transfer"""
            c.execute(sequence)

            # update echipa veche
            c.execute("SELECT id_echipa FROM Jucatori WHERE id_jucator = " + id_player)
            id0 = c.fetchall()
            if id0[0][0] != 0:
                sequence = """ UPDATE  Echipe 
                            SET nr_jucatori = nr_jucatori - 1,
                            buget = buget + (SELECT salariu FROM Jucatori WHERE id_jucator = """ + id_player + ")" + """ 
                            WHERE id_echipa = (SELECT id_echipa 
                            from Jucatori where id_jucator =""" + id_player + ")"
                c.execute(sequence)
            else:
                sequence = """ UPDATE  Echipe 
                                            SET nr_jucatori = nr_jucatori - 1 
                                            WHERE id_echipa = 0"""
                c.execute(sequence)
            # conn.commit()

            # update jucator
            sequence = """ UPDATE  Jucatori SET id_echipa = """ + id_echipa + ", status = 1 WHERE id_jucator = " \
                       + id_player
            c.execute(sequence)
            # conn.commit()

            # update echipa noua
            sequence = """ UPDATE  Echipe SET  buget = buget -""" + salary + " , nr_jucatori  = nr_jucatori + 1 " \
                                                                             "WHERE id_echipa = " + id_echipa
            c.execute(sequence)

            # conn.commit()


def transactionPressed():
    id_echipa = (id_team_transaction.get()[0] + id_team_transaction.get()[1]).rstrip()
    transaction = tk.Tk()

    transaction.title("Tranzactie")
    transaction.geometry("250x130")

    # Creeare chenare
    c = conn.cursor()
    c.execute("SELECT buget FROM echipe WHERE id_echipa = " + id_echipa)
    row = c.fetchall()
    tk.Label(transaction, text="Buget Disponibil:" + str(row[0][0])).grid(row=0)
    tk.Label(transaction, text="Nume Jucator").grid(row=1)

    # Choice Box for id players
    c = conn.cursor()
    sequence = """ SELECT id_jucator, prenume, nume, salariu FROM Jucatori WHERE status = 0 AND  id_echipa != """ + id_echipa
    c.execute(sequence)
    row = c.fetchall()

    variable = StringVar(root)
    variable.set('1')
    transaction_player = Combobox(transaction, values=row)
    transaction_player.grid(row=1, column=1)

    transaction_button = Button(transaction, text="Transfera",
                                command=lambda: transaction_function(id_echipa, transaction_player))
    transaction_button.place(x=100, y=60)


if __name__ == "__main__":
    # create connection
    conn = cx_Oracle.connect('matei/bd059@//localhost:1521/xe')
    print(conn.version)

    # create cursor
    cursor = conn.cursor()

    root = tk.Tk()

    root.title("Tema baza de date")
    root.geometry("400x180")
    root.configure(background='red')
    style = ThemedStyle(root)
    style.set_theme("clearlooks")
    tabControl = ttk.Notebook(root)
    tab_players = ttk.Frame(tabControl)
    tab_teams = ttk.Frame(tabControl)
    tab_details = ttk.Frame(tabControl)
    tab_history = ttk.Frame(tabControl)
    tab_positions = ttk.Frame(tabControl)
    tab_transaction = ttk.Frame(tabControl)

    tabControl.add(tab_players, text='Jucatori')
    tabControl.add(tab_teams, text='Echipe')
    tabControl.add(tab_details, text='Detalii Jucatori')
    tabControl.add(tab_history, text='Istorie')
    tabControl.add(tab_positions, text='Pozitii')
    tabControl.add(tab_transaction, text='Tranzactie')

    tabControl.pack(expand=1, fill="both")

    ##################

    addPlayer = Button(tab_players, text="Adauga Jucator", command=addPressed_player)
    addPlayer.pack(side=TOP)

    delPlayer = Button(tab_players, text="Sterge un jucator", command=deletePressed_player)
    delPlayer.pack(side=TOP)

    modifyPlayer = Button(tab_players, text="Modifica un jucator", command=modifyPressed_player)
    modifyPlayer.pack(side=TOP)

    visualizePlayer = Button(tab_players, text="Vizualizeaza jucatori", command=visualizePressed_player)
    visualizePlayer.pack(side=TOP)

    ##################

    addTeam = Button(tab_teams, text="Adauga Echipa", command=addPressed_team)
    addTeam.pack(side=TOP)

    delTeam = Button(tab_teams, text="Sterge Echipa", command=deletePressed_team)
    delTeam.pack(side=TOP)

    modifyTeam = Button(tab_teams, text="Modifica Echipa", command=modifyPressed_team)
    modifyTeam.pack(side=TOP)

    visualizeTeam = Button(tab_teams, text="Vizualizeaza echipe", command=visualizePressed_team)
    visualizeTeam.pack(side=TOP)

    ###################

    addDetails = Button(tab_details, text="Adauga Detalii Jucatori", command=addPressed_details)
    addDetails.pack(side=TOP)

    delDetails = Button(tab_details, text="Sterge Detalii Jucatori", command=deletePressed_details)
    delDetails.pack(side=TOP)

    modifyDetails = Button(tab_details, text="Modifica Detaliile Jucatori", command=modifyPressed_details)
    modifyDetails.pack(side=TOP)

    visualizeDetails = Button(tab_details, text="Vizualizeaza detaliile jucatorilor", command=visualizePressed_details)
    visualizeDetails.pack(side=TOP)

    ###################

    addHistory = Button(tab_history, text="Adauga Istorie", command=addPressed_history)
    addHistory.pack(side=TOP)

    delHistory = Button(tab_history, text="Sterge Istoric Jucator",
                        command=lambda: modify_or_deletePressed_history(switch=0))
    delHistory.pack(side=TOP)

    modifyHistory = Button(tab_history, text="Modifica Istoric Jucatori",
                           command=lambda: modify_or_deletePressed_history(switch=1))
    modifyHistory.pack(side=TOP)

    visualizeHistory = Button(tab_history, text="Vizualizeaza istoricul jucatorilor", command=visualizePressed_history)
    visualizeHistory.pack(side=TOP)

    ###################

    visualizePosition = Button(tab_positions, text="Vizualizeaza Pozitiile", command=visualizePressed_positions)
    visualizePosition.place(relx=0.5, rely=0.5, anchor=CENTER)

    ####################
    tk.Label(tab_transaction, text="ID Echipa").grid(row=0)

    # Choice Box for id players
    c_transaction = conn.cursor()
    sequence_transaction = """ SELECT id_echipa, nume_echipa FROM Echipe WHERE id_echipa != 0"""
    c_transaction.execute(sequence_transaction)
    row_transaction = c_transaction.fetchall()
    variable_transaction = StringVar(root)
    variable_transaction.set('1')
    id_team_transaction = Combobox(tab_transaction, values=row_transaction)
    id_team_transaction.grid(row=0, column=1)

    transactionPlayer = Button(tab_transaction, text="Tranzactie Jucator", command=transactionPressed).place(x=90, y=40)
    # transactionPlayer.pack(side=TOP)

    root.mainloop()
