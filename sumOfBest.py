from lxml import etree
import sys
import PySimpleGUI as sg

def TimeFormatter(time, pos):
    h = int(time / 3600)
    m = int((time % 3600) / 60)
    s = int((time % 3600) % 60)
    if h > 0:
        return "%dh %dm %ds" % (h, m, s)
    elif m > 0:
        return "%dm %ds" % (m, s)
    return "%ds" % (s)
    
def TimeToValue(inTime):
    [hours, minutes, seconds] = [float(x) for x in inTime.split(':')]
    return hours*3600.0 + minutes*60.0 + seconds

def GetSegmentName(inSegment):
    return inSegment.find("Name").text

def AllSegments():
    allSegments = tree.find("Segments")
    for Seg in tree.find("Segments"):
        yield Seg

def BuildSegmentsById(inTree):
    outTable = dict()
    for Seg in AllSegments():
        segName = GetSegmentName(Seg)
        segHist = Seg.find("SegmentHistory")
        
        if not segName in outTable:
            outTable[segName] = dict()
        
        for time in segHist:
            id = time.attrib["id"]
            if int(id) > 0:
                realTimeSeg = time.find("RealTime")
                if realTimeSeg is not None:
                    realTime = TimeToValue(realTimeSeg.text)
                    outTable[segName][id] = realTime
                
                
    return outTable

def GetBestSegment(allSegments, names, startIdx, endIdx):
    startSegment = allSegments[names[startIdx+1]]
    
    sum = 0
    minSegLen = None
    for runId in startSegment:
        segLen = 0
        for k in range(startIdx + 1, endIdx + 1):
            if runId in allSegments[names[k]]:
                segLen += allSegments[names[k]][runId]
            else:
                segLen = None
                break
        if segLen:
            minSegLen = min(segLen, minSegLen) if minSegLen else segLen
    return minSegLen

def CalculateSumOfBest(splits):
    v = BuildSegmentsById(tree)
    names = list(v)
    sum = 0
    
    p = -1
    for s in range(len(splits)):
        n = names.index(splits[s])
        b = GetBestSegment(v, names, p, n)
        sum += b
        p = n
        
    return TimeFormatter(sum, 0)

def GetSplitNames():
    v = BuildSegmentsById(tree)
    return list(v)

if len(sys.argv) == 1:
    print("Please specify a file path.")
    exit()
    
GFileName = ' '.join(sys.argv[1:])
    
tree = etree.parse(GFileName)

names = GetSplitNames()
layout = [[sg.Text('Sum of best: ', key='sob', size=(20, 1), auto_size_text=True)], [sg.Listbox(names, enable_events=True, size=(None, len(names)), key='list_changed', select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE)]]
sg.theme('DarkBlue')
window = sg.Window('Sum of best', layout, keep_on_top=True, resizable=False, finalize=True, icon='stashio.ico')
window['sob'].expand(expand_x=True)

while True:
    event, values = window.Read()
    if not event:
        break
    if event == 'list_changed':
        c = CalculateSumOfBest(values['list_changed'])
        window['sob'].update(f'Sum of best: {c}')