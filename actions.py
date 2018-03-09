import datetime, calendar, json
from telepot.namedtuple import InlineKeyboardButton, InlineKeyboardMarkup

def test():
    print "test"


def checkInToday(userId):
    '''
        Find user group and check that he coming
    :param userId:
    :return:
        0 - OK
        1 - user have no group
        2 - user already checked before
        5 - Try add users to today's group. Can't find group in emplee.json
    '''
    weekDay = calendar.day_name[datetime.datetime.now().weekday()]


    ##--- find the group of worker
    managerId = 0
    employee = json.load(open('employee.json'))
    for groups in employee['groups']:
        if userId in employee['groups'][groups]:
            managerId = groups
            break
    print managerId

    if managerId == 0:
        print "User {} have no group.".format(userId)
        return 1


    checkIn = json.load(open('checkIn.json'))

    ###--- add new weekday
    if not weekDay in checkIn['date']:
        print "There no {} in 'Date'. New weekday is added".format(weekDay)
        checkIn['date'].update({str(weekDay):{}})
        with open('checkIn.json', 'w') as fileName:
            json.dump(checkIn, fileName, indent=2)

    ###---- add group in weekday. And set 'Active': 0 to all users
    if not str(managerId) in checkIn['date'][weekDay]:
        employee = json.load(open('employee.json'))
        if not str(managerId) in employee['groups']:
            print "Try add users to today's group. Can't find group in emplee.json"
            return 5

        allUsers = {}
        for user in employee['groups'][str(managerId)]:
            allUsers.update({str(user):{"active":0}})
        checkIn['date'][weekDay].update({str(managerId):allUsers})
        with open('checkIn.json', 'w') as fileName:
            json.dump(checkIn, fileName, indent=2)

        print "There no group {} in day {}. New group is added".format(managerId, weekDay)


    ###--- need update today's note if userId is empty
    if not str(userId) in checkIn['date'][weekDay][managerId]:
        checkIn['date'][weekDay][managerId].update({str(userId):{"active":0}})
        with open('checkIn.json', 'w') as fileName:
            json.dump(checkIn, fileName, indent=2)

    ###--- there is no 'Active' in user field
    if not "active" in checkIn['date'][weekDay][managerId][str(userId)]:
        print "Checkin.json not contain field  'Active' for user {}. Added 'Active' ".format(userId)
        checkIn['date'][weekDay][managerId][str(userId)].update({"active":0})
        with open('checkIn.json', 'w') as fileName:
            json.dump(checkIn, fileName, indent=2)

    ###--- change activity
    if checkIn['date'][weekDay][managerId][str(userId)]["active"] == 0:
        checkIn['date'][weekDay][managerId][str(userId)]["active"] = 1
    else:
        print "User already checked"
        return 2



    with open('checkIn.json', 'w') as fileName:
        json.dump(checkIn, fileName, indent=2)
    return  0

def getCheckedWorkerList(managerId):
    '''
        Return list with users and show wich of them was checked

    :param managerId:
    :return:
        workerList[] - OK
        1 - employee.json have no group with this managerId
        2 - group is empty
    '''

    # workerList = {}
    # employee = json.load(open('employee.json'))
    # if str(managerId) in employee['groups']:
    #     workerList = employee['groups'][str(managerId)]
    # else:
    #     print "Manager not registered"
    #     return 1
    # print workerList
    #
    # if workerList == []:
    #     print "Group is empty"
    #     return 2

    weekDay = calendar.day_name[datetime.datetime.now().weekday()]
    tomorrow = calendar.day_name[datetime.datetime.now().weekday()-6]

    checkIn = json.load(open('checkIn.json'))

    ##--- delete tomorrow field
    if tomorrow in checkIn['date']:
        checkIn['date'].pop(tomorrow)
        with open('checkIn.json', 'w') as fileName:
            json.dump(checkIn, fileName, indent=2)

    ###--- add today weekday
    if not weekDay in checkIn['date']:
        print "There no {} in 'Date'. New weekday is added".format(weekDay)
        checkIn['date'].update({str(weekDay):{}})
        with open('checkIn.json', 'w') as fileName:
            json.dump(checkIn, fileName, indent=2)

    ###---- add group in weekday. And set 'Active': 0 to all users
    if not str(managerId) in  checkIn['date'][weekDay]:
        employee = json.load(open('employee.json'))
        if not str(managerId) in employee['groups']:
            print "Try add users to today's group. Can't find group in emplee.json"
            return 5

        allUsers = {}
        for user in employee['groups'][str(managerId)]:
            allUsers.update({str(user): {"active": 0}})
        checkIn['date'][weekDay].update({str(managerId): allUsers})
        with open('checkIn.json', 'w') as fileName:
            json.dump(checkIn, fileName, indent=2)

        print "There no group {} in day {}. New group is added".format(managerId, weekDay)
    workerList = checkIn['date'][weekDay][str(managerId)]
    if workerList == {}:
        print "Group is empty"
        return 2

    # workerReturn = {}
    # for worker in workerList:
    #     if 'active' in workerList[worker]:
    #         workerReturn.update({worker:workerList[worker]})
    # return workerReturn

    return workerList


def parseWorkerList(workerList):
    strWorkerList = ""
    for worker in workerList:
        if 'active' in workerList[worker]:
            strWorkerList += str(worker)+ ": " + str(workerList[worker]['active']) + "\n"

    return strWorkerList




def addNewWorker(userId, userName, first_name):
    employee = json.load(open('employee.json'))

    if str(userId) in employee['workers2']:
        print "User already in workers"
        return 1

    if userId in employee['managers']:
        print "User already in Managers"
        return 2

    newUser = {str(userId):{"name":userName, "first_name":first_name}}
    print employee
    employee['workers2'].update(newUser)
    print  employee

    with open('employee.json', 'w') as fileName:
        json.dump(employee, fileName, indent=2)

    return 0

def addNewMnager(userId):
    employee = json.load(open('employee.json'))
    if str(userId) in employee['workers2']:
        print "User already in workers"
        return 1

    if userId in employee['managers']:
        print "User already in Managers"
        return 2

    employee['managers'].append(userId)
    employee['groups'].update({str(userId):[]})

    with open('employee.json', 'w') as fileName:
        json.dump(employee, fileName, indent=2)

    return 0



def connectWorkerToManager(userId, managerId):
    '''
        Add worker to group with manager
    :param userId:
    :param managerId:
    :return:
        0 - OK
        1 - there is no group
        2 -there is no user in workers
        group:number - User already in group
    '''
    print  "Add user {} to group with manager {}".format(userId, managerId)
    employee = json.load(open('employee.json'))

    if not str(managerId) in employee['groups']:
        print "There is no group"
        return 1

    if not str(userId) in employee['workers2']:
        print "There is no user {} in workers". format(userId)
        return 2

    for group in employee['groups']:
        if userId in employee['groups'][group]:
            print "User {} already in group {}".format(userId, group)
            return "group:{}".format(group)

    ##-- add to group and save
    employee['groups'][str(managerId)].append(userId)

    with open('employee.json', 'w') as fileName:
        json.dump(employee, fileName, indent=2)


    return 0


def getGroupList():
    employee = json.load(open('employee.json'))
    groupList = []
    for group in employee["groups"]:
        groupList.append(group)
    return groupList

def parseGroupToButtons(groupList):
    keyboard = []
    for group in groupList:
        print group
        # button = InlineKeyboardButton(text='as' callback_data='_manager_:{}'.format(group))
        button = [InlineKeyboardButton(text='{}'.format(group), callback_data='_manager_:{}'.format(group))]
        keyboard.append(button)

    return keyboard



def deleteUser(userId):
    employee = json.load(open('employee.json'))

    if str(userId) in employee['workers2']:
        employee['workers2'].pop(str(userId))

    if userId in employee['managers']:
        employee['managers'].remove(userId)

    if str(userId) in employee['groups']:
        employee['groups'].pop(str(userId))

    for group in employee['groups']:
        if userId in employee['groups'][str(group)]:
            employee['groups'][str(group)].remove(userId)

    ##-- save changes
    with open('employee.json', 'w') as fileName:
        json.dump(employee, fileName, indent=2)

    # {
    #     "workers": [
    #         290350174
    #     ],
    #     "managers": [
    #         526522833,
    #         526522832
    #     ],
    #     "workers2": {
    #         "290350174": {
    #             "name": "Ver1Sus"
    #         },
    #         "290350175": {
    #             "first_name": "Valeriy",
    #             "name": "Ver1Sus"
    #         },
    #         "12": {
    #             "first_name": "e",
    #             "name": ""
    #         }
    #     },
    #     "groups": {
    #         "526522832": [
    #             4,
    #             290350174
    #         ],
    #         "526522833": [
    #             3,
    #             5,
    #             290350175
    #         ]
    #     }
    # }

    return 0

if __name__ == '__main__':
    # print checkInToday(290350175)
    # print parseWorkerList(getCheckedWorkerList(526522833))
    # addNewWorker(12, "", "e")
    # print connectWorkerToManager(290350174, 526522832)
    # print parseGroupToButtons(getGroupList())
    # deleteUser(5)
    print  addNewMnager(5)