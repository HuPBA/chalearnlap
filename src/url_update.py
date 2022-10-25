from chalearnlap.users.models import Event, Track


def replace_data():
	for event in Event.objects.filter(description__contains='http://158.109.8.102').all():
		event.description = event.description.replace('http://158.109.8.102', 'https://data.chalearnlap.cvc.uab.cat')
		event.save()	


def replace_local():
        for event in Event.objects.filter(description__contains='http://chalearnlap.cvc.uab').all():
                event.description = event.description.replace('http://chalearnlap.cvc.uab', 'https://chalearnlap.cvc.uab')
                event.save()


def replace_track():
        for track in Track.objects.filter(description__contains='http://chalearnlap.cvc.uab').all():
                track.description = track.description.replace('http://chalearnlap.cvc.uab', 'https://chalearnlap.cvc.uab')
                track.description = track.description.replace('http://158.109.8.102', 'https://data.chalearnlap.cvc.uab.cat')
                track.save()



def replace_event_data(source, destination):
        for event in Event.objects.filter(description__contains=source).all():
                event.description = event.description.replace(source, destination)
                event.save()


def replace_track_data(source, destination):
        for track in Track.objects.filter(description__contains=source).all():
                track.description = track.description.replace(source, destination)                
                track.save()


def update_data():

	replacements = [
		('http://158.109.8.102', 'https://data.chalearnlap.cvc.uab.cat'),
		('http://chalearnlap.cvc.uab', 'https://chalearnlap.cvc.uab'),
		('http://jmlr.org', 'https://jmlr.org'),
		('http://gesture.chalearn.org', 'https://gesture.chalearn.org'),
		('http://www.springer.com', 'https://www.springer.com'),
		('http://image-net.org', 'https://image-net.org'),
		('http://icmi.acm.org', 'https://icmi.acm.org'),
		('http://www.youtube.com', 'https://www.youtube.com'),
		('http://competitions.codalab.org', 'https://competitions.codalab.org'),
	]

	for rep_src, rep_dst in replacements:
		print('{} -> {}'.format(rep_src, rep_dst))
		replace_event_data(rep_src, rep_dst)
		replace_track_data(rep_src, rep_dst)

	list_pending()


def get_event_type(event):
	try:
		event.special_issue.id
		return 'special_issue'
	except Exception:
		pass
	try:
                event.workshop.id
                return 'workshop'
        except Exception:
                pass
	try:
                event.challenge.id
                return 'challenge'
        except Exception:
                pass
	

	return 'unknown'

def list_pending():

	for event in Event.objects.filter(description__contains='http://').all():
		url_start = event.description.find('http://')
		url_end = min(len(event.description) - 1, url_start + 50)
		try:
			print('Event {} (https://chalearnlap.cvc.uab.cat/{}/{}/description/) => {}'.format(event.id, get_event_type(event), event.id, event.description[url_start:url_end]))
		except Exception as exc:
			print('Event {} (https://chalearnlap.cvc.uab.cat/{}/{}/description/) => {}'.format(event.id, get_event_type(event), event.id, str(exc)))

        for track in Track.objects.filter(description__contains='http://').all():
		url_start = track.description.find('http://')
		url_end = min(len(track.description) - 1, url_start + 50)
		try:
	                print('Track {} => {}'.format(track.id, track.description[url_start:url_end]))
		except Exception as exc:
			print('Track {} => {}'.format(track.id, track.description[url_start:url_end], str(exc)))
