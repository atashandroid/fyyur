from starter_code.app import Venue, db


def ven_v():
    celine_dion = Venue(
        id=1,
        name='Celine Dion',
        city='Charlemagne',
        state='Québec',
        address='Charlemagne, Québec',
        phone='998-93-8548565',
        image_link='https://cdn.smehost.net/celinedioncom-caprod/wp-content/uploads/2019/03/about-1991-23-ans-555x672.jpg',
        facebook_link='https://www.facebook.com/celinedion/',
        genres='pop',
        website='https://www.celinedion.com/about/biography/',
        seeking_talent=False,
        seeking_description='That summer Celine embarked on a two-month tour of the Asia-Pacific region'
    )
    db.session.add(celine_dion)
    db.session.commit()
    db.session.close()


if __name__ == '__main__':
    print('Populating db...')
    ven_v()
    print('Successfully populated!')
