from pathlib import Path
import json

class FormatMetadata:
    '''Formats metadata for grammatical consistancy'''
    functors = ['a', 'an', 'the', 'in', 'on', 'at', 'by', 'and', 
                'but', 'or', 'you', 'your', 'my', 'his', 'her', 
                'their', 'this', 'that', 'these', 'those', 'what', 
                'which', 'who', 'there', 'can', 'will', 'should', 
                'would', 'must', 'may', 'might', 'could', 'not', 
                'no', 'to']

    def __init__(self):
        assert Path('results.json').is_file(), 'Missing results.json'
        with open('results.json', 'rb') as f:
            self.data = json.load(f)
        
        self.author, self.title = '', ''

        self.volume_info = (values['volumeInfo'] for values in self.data['items'])
    
    def std_title(self, title):
        '''Modifies variable str to check grammatical functors'''
        format_title = [title.split(' ')[0]]
        for word in title.split(' ')[1:]:
            if word.lower() in self.functors:
                format_title.append(word.lower())
            else: format_title.append(word)
        
        return ' '.join(format_title)

    def format_metadata(self):
        '''Formats desired metadata from JSON'''
        current = next(self.volume_info)

        title = self.std_title(current['title'])
        if current.get('subtitle'): 
            subtitle = self.std_title(current['subtitle'])
            title += ': {value}'.format(value=subtitle)
        
        if len(current['authors']) == 3:
            author = ', '.join(current['authors'][:-1]) + 'and ' + current['authors'][-1]
        elif len(current['authors']) == 1: 
            author = current['authors'][0]
        elif len(current['authors']) >= 4: 
            author = current['authors'][0] + ' and Others'
        else: author = current['authors'][0] + ' and ' + current['authors'][-1]

        self.confirm_metadata(author, title)

    def confirm_metadata(self, author, title):
        '''Confirm if given metadata is correct'''
        accepted_resp = ['yes', 'y']
        print('Found \"{title}\" by {author}'.format(title=title, author=author))
        confirm = input('Is this ok? (y/n) ').lower()

        if confirm not in accepted_resp:
            try: self.format_metadata()
            except StopIteration:
                print('Out of results')
        else: self.author, self.title = author, title
    
    def metadata(self):
        '''Returns accepted metadata in a tuple'''
        return self.author, self.title