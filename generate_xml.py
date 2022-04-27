#!/usr/bin/env python3

import os

from lxml import etree
from urllib import parse as url

import argparse

IGNORED_EVENTS = [
    'EVENT:START RECORDING',
    'EVENT:STOP RECORDING',
    'EVENT:RECORDING PAUSED',
    'EVENT:SCENE CHANGED'
]

TODO_EVENTS = [
    'RECORDING RESUMED',
    'HOTKEY'
]

REF_INDEX = 0

def get_ref():
    global REF_INDEX
    REF_INDEX += 1
    return f'r{REF_INDEX}'

def generate_xml(video_list, event_name):
    root = etree.Element('fcpxml')
    root.attrib['version'] = '1.10'

    resources_tag = etree.SubElement(root, 'resources')    

    event_tag = etree.SubElement(root, 'event')    
    event_tag.attrib['name'] = event_name

    project_tag = etree.SubElement(event_tag, 'project')
    project_tag.attrib['name'] = 'Untitled Project'

    sequence_tag = etree.SubElement(project_tag, 'sequence')
    sequence_tag.attrib['format'] = 'r1'

    spine_tag = etree.SubElement(sequence_tag, 'spine')

    format_tag = etree.SubElement(resources_tag, 'format')
    format_tag.attrib['id'] = get_ref()
    format_tag.attrib['name'] = 'FFVideoFormat1080p60'

    for (video, log) in video_list:
        ref = get_ref()
        video_basename = os.path.basename(video)

        asset_tag = etree.SubElement(resources_tag, 'asset')
        asset_tag.attrib['id'] = ref
        asset_tag.attrib['name'] = f'{video_basename} original'


        media_rep_tag = etree.SubElement(asset_tag, 'media-rep')
        media_rep_tag.attrib['kind'] = 'original-media'
        # media_rep_tag.attrib['src'] = video_url
        media_rep_tag.attrib['src'] = url.quote(video_basename)

        asset_clip_tag = etree.SubElement(event_tag, 'asset-clip')
        asset_clip_tag.attrib['name'] = video_basename
        asset_clip_tag.attrib['ref'] = ref

        # Loop through log and add markers

        log_text = open(log, 'r').read()
        for log_item in log_text.split('\n\n'):
            log_item_split = log_item.split('\n')
            if (len(log_item_split) < 3):
                continue

            event_name, record_time_str, stream_time_str = log_item_split

            if True in [ignored_event in event_name for ignored_event in IGNORED_EVENTS]:
                continue

            record_hours, record_minutes, record_seconds = [int(x) for x in record_time_str.split(' ')[0].split(':')]
            record_total_seconds = record_seconds + record_minutes * 60 + record_hours * 60 * 60

            marker_tag = etree.SubElement(asset_clip_tag, 'marker')
            marker_tag.attrib['value'] = event_name
            marker_tag.attrib['start'] = f'{record_total_seconds}s'
            marker_tag.attrib['duration'] = '1000/30000s'

            if True in [todo_event in event_name for todo_event in TODO_EVENTS]:
                marker_tag.attrib['completed'] = '0'

            # print(f'event: {event_name}')
            # print(f'record_time: {record_total_seconds}s')
            # print('---')

    return root

def process_files(event_title, file_tuple_list):
    os.mkdir(f'{event_title}.fcpxmld')

    for video_file, log_file in file_tuple_list:
        os.rename(video_file, f'{event_title}.fcpxmld/{os.path.basename(video_file)}')

    fcpxml = generate_xml(file_tuple_list, event_title)

    with open(f'{event_title}.fcpxmld/Info.fcpxml', 'w') as f:
        print('<?xml version="1.0" encoding="UTF-8"?>', file=f)
        print('<!DOCTYPE fcpxml>', file=f)
        print('', file=f)
        print(etree.tostring(fcpxml, pretty_print=True).decode('UTF-8'), file=f)

    global REF_INDEX
    REF_INDEX = 0

parser = argparse.ArgumentParser(description='Generate FCPXML from OBS Infowriter output')
parser.add_argument('event_title')
parser.add_argument('file_list', nargs='+', help='video file, log file ...')

if __name__ == '__main__':
    args = parser.parse_args()

    if len(args.file_list)%2 != 0:
        print('One log must be provided for each video')
        print(args.file_list)
        print(len(args.file_list))
        print(len(args.file_list)%2)
        exit(1)

    file_tuple_list = []

    for i in range(0, len(args.file_list), 2):
        video_file = args.file_list[i]
        log_file = args.file_list[i+1]
        file_tuple_list.append((video_file, log_file))

    process_files(args.event_title, file_tuple_list)
