import os
import re
import zipfile

from collections import OrderedDict

re_tc = re.compile(r'.+?\.(?P<sample>sample\.|dummy\.)?(?P<type>in|out)\.(?P<number>\d+)(?P<letter>[a-z])?$')

# SETTINGS
year = r''

def gen_tuple(x):
	m = re_tc.match(x)
	return (not bool(m.group('sample')), int(m.group('number')), m.group('letter') or '')


for contest in os.listdir(year):
	for problem in os.listdir(os.path.join(year, contest)):
		path = os.path.join(year, contest, problem)
		
		zipname = None
		for file in os.listdir(path):
			if file.endswith('.zip'):
				zipname = file
				break
		else:
			files = os.listdir(path)
			zipname = problem + '.zip'
			zip = zipfile.ZipFile(os.path.join(path, zipname), 'w', zipfile.ZIP_DEFLATED)
			for file in files:
				zip.write(os.path.join(path, file), file)
				os.remove(os.path.join(path, file))
			zip.close()

		zip = zipfile.ZipFile(os.path.join(path, zipname))
		
		files = zip.namelist()
		files = sorted(files, key = lambda x:gen_tuple(x))
		
		# Store in an OrderedDict
		M = OrderedDict()
		
		for file in files:
			m = re_tc.match(file)
			
			n = int(m.group('number'))
			l = m.group('letter')
			
			if m.group('sample'):
				M.setdefault(0, OrderedDict())
				M[0].setdefault(n, dict())
				M[0][n][m.group('type')] = file
			else:
				M.setdefault(n, OrderedDict())
				M[n].setdefault(l, dict())
				M[n][l][m.group('type')] = file
		
		with open(os.path.join(path, 'init.yml'), 'w') as f:
		
			f.write('archive: %s\n' % zipname)
			f.write('test_cases:\n')
			
			for batchnum, batch in M.iteritems():
				if len(batch) > 1:
					f.write('- batched:\n')
				
				for case in batch.values():
					if len(batch) > 1:
						f.write('  ')
					try:
						f.write('- {in: %s, out: %s' % (case['in'], case['out']))
					except KeyError:
						f.write('- {in: %s' % case['in'])
					if len(batch) == 1:
						f.write(', points: %d' % int(bool(batchnum)))
					f.write('}\n')
					
				if len(batch) > 1:
					f.write('  points: %d\n' % int(bool(batchnum)))
				
		zip.close()
