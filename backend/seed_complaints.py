import sys
import os
from datetime import datetime, timezone, timedelta

# Add parent dir to path so we can import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal, engine, Base
from backend.models import Complaint
from backend.data.department_emails import get_department_email
from backend.data.municipalities import lookup_municipality

# Create tables just in case
Base.metadata.create_all(bind=engine)

def create_mock_complaints():
    session = SessionLocal()
    
    # Check if we already have complaints
    if session.query(Complaint).count() > 0:
        print("Database already contains complaints. Adding more anyway.")

    complaints_data = [
        {
            "transcribed_text": "Има огромна дупка на улица Иван Вазов, колите си трошат гумите.",
            "category": "ROADS",
            "location_mentioned": "Ботевград",
            "urgency": "HIGH",
            "formal_letter": "Уважаеми господине/госпожо,\n\nБих искал да подам сигнал относно опасна дупка на пътната настилка на улица 'Иван Вазов'. Проблемът създава сериозна предпоставка за пътнотранспортни произшествия и нанася щети на автомобилите.\n\nМоля за вашето съдействие за своевременното отстраняване на проблема.\n\nС уважение,\nЗагрижен гражданин",
            "days_ago": 0
        },
        {
            "transcribed_text": "Водата е спряла от два дена в квартал Изток, никой не вдига телефоните.",
            "category": "WATER_SUPPLY",
            "location_mentioned": "Своге",
            "urgency": "HIGH",
            "formal_letter": "Уважаеми господине/госпожо,\n\nОбръщам се към вас във връзка с прекъснато водоподаване в квартал Изток повече от 48 часа. Липсата на вода създава сериозни битови и санитарни неудобства.\n\nНастоявам за бърза проверка и възстановяване на водоподаването.\n\nС уважение,\nЗагрижен гражданин",
            "days_ago": 1
        },
        {
            "transcribed_text": "Контейнерите за боклук пред блока преливат, не са изхвърляни от седмица.",
            "category": "WASTE_MANAGEMENT",
            "location_mentioned": "Елин Пелин",
            "urgency": "MEDIUM",
            "formal_letter": "Уважаеми господине/госпожо,\n\nПодавам сигнал за препълнени контейнери за битови отпадъци пред жилищния ни блок. Отпадъците не са извозвани повече от седмица, което води до неприятни миризми и риск от развъждане на вредители.\n\nМоля за незабавно сметоизвозване.\n\nС уважение,\nЗагрижен гражданин",
            "days_ago": 1
        },
        {
            "transcribed_text": "Уличното осветление на централната алея не работи и е много тъмно вечер.",
            "category": "ELECTRICITY",
            "location_mentioned": "Сливница",
            "urgency": "LOW",
            "formal_letter": "Уважаеми господине/госпожо,\n\nБих искал да ви уведомя, че уличното осветление по централната алея не функционира. Липсата на осветление създава дискомфорт и чувство за несигурност у преминаващите граждани през тъмната част на денонощието.\n\nМоля да бъде изпратен екип за подмяна на осветителните тела.\n\nС уважение,\nЗагрижен гражданин",
            "days_ago": 2
        },
        {
            "transcribed_text": "Съседите вдигат страшен шум всяка вечер след 23 часа, пускат силна музика.",
            "category": "PUBLIC_ORDER",
            "location_mentioned": "Божурище",
            "urgency": "MEDIUM",
            "formal_letter": "Уважаеми господине/госпожо,\n\nПодавам сигнал за системно нарушаване на обществения ред и тишината в часовете за почивка (след 23:00 ч.) от страна на мои съседи, които пускат силна музика.\n\nМоля да извършите проверка и да предприемете необходимите мерки съгласно наредбите за обществения ред.\n\nС уважение,\nЗагрижен гражданин",
            "days_ago": 2
        },
        {
            "transcribed_text": "Тревата в парка зад общината е много висока и има кърлежи, децата не могат да играят.",
            "category": "GREEN_SPACES",
            "location_mentioned": "Драгоман",
            "urgency": "MEDIUM",
            "formal_letter": "Уважаеми господине/госпожо,\n\nСигнализирам за неокосена висока трева в парка зад сградата на общината. Състоянието на зелените площи е предпоставка за развъждане на кърлежи и прави мястото опасно за играещите деца.\n\nМоля за спешно окосяване и пръскане срещу вредители.\n\nС уважение,\nЗагрижен гражданин",
            "days_ago": 3
        },
        {
            "transcribed_text": "Няма кой да ми издаде скица на имота вече втори месец, служителката все е в болничен.",
            "category": "ADMINISTRATIVE",
            "location_mentioned": "Ихтиман",
            "urgency": "LOW",
            "formal_letter": "Уважаеми господине/госпожо,\n\nБих искал да изразя недоволството си относно забавяне при издаването на административна услуга - скица на имот. Процедурата се бави повече от два месеца поради отсъствие на служител, без да е осигурен заместник.\n\nМоля за съдействие за по-бързото приключване на преписката.\n\nС уважение,\nЗагрижен гражданин",
            "days_ago": 4
        },
        {
            "transcribed_text": "Избягало куче от съседен двор плаши минувачите по улицата.",
            "category": "OTHER",
            "location_mentioned": "Костинброд",
            "urgency": "MEDIUM",
            "formal_letter": "Уважаеми господине/госпожо,\n\nУведомявам ви за свободно разхождащо се голямо куче, което е излязло от частен двор и създава страх сред преминаващите граждани по улицата.\n\nМоля да бъде извършена проверка и да се вземат мерки за безопасността на пешеходците.\n\nС уважение,\nЗагрижен гражданин",
            "days_ago": 4
        },
        {
            "transcribed_text": "Пропаднала шахта на тротоара пред детската градина, много е опасно за децата.",
            "category": "ROADS",
            "location_mentioned": "Долна Баня",
            "urgency": "HIGH",
            "formal_letter": "Уважаеми господине/госпожо,\n\nСигнализирам за пропаднала и необезопасена шахта, намираща се на тротоара в непосредствена близост до детската градина. Това представлява изключително голяма опасност за здравето на децата и техните родители.\n\nНастоявам за спешно обезопасяване и ремонт на съоръжението.\n\nС уважение,\nЗагрижен гражданин",
            "days_ago": 5
        },
        {
            "transcribed_text": "Чешмичката в центъра тече непрекъснато и наводнява площада.",
            "category": "WATER_SUPPLY",
            "location_mentioned": "Годеч",
            "urgency": "LOW",
            "formal_letter": "Уважаеми господине/госпожо,\n\nБих искал да ви обърна внимание на проблем с обществената чешма в центъра на града. Кранът е повреден и водата тече непрекъснато, което води до разхищение на питейна вода и наводняване на околното пространство.\n\nМоля повредата да бъде отстранена.\n\nС уважение,\nЗагрижен гражданин",
            "days_ago": 5
        },
        {
            "transcribed_text": "Силна миризма на изгорели гуми в района на старата фабрика.",
            "category": "WASTE_MANAGEMENT",
            "location_mentioned": "Костенец",
            "urgency": "HIGH",
            "formal_letter": "Уважаеми господине/госпожо,\n\nПодавам сигнал за силно и задушливо замърсяване на въздуха. Усеща се остра миризма на изгорели гуми и пластмаса в района на старата фабрика.\n\nНастоявам за незабавна проверка от страна на екоинспектората за установяване и санкциониране на нарушителите.\n\nС уважение,\nЗагрижен гражданин",
            "days_ago": 6
        },
        {
            "transcribed_text": "Паднало дърво след снощната буря е блокирало пътя към съседното село.",
            "category": "GREEN_SPACES",
            "location_mentioned": "Горна Малина",
            "urgency": "HIGH",
            "formal_letter": "Уважаеми господине/госпожо,\n\nУведомявам ви, че вследствие на силния вятър снощи е паднало голямо дърво, което напълно блокира пътното платно в посока към съседното село.\n\nМоля за спешно изпращане на екип, който да нареже дървото и да освободи пътя за движение.\n\nС уважение,\nЗагрижен гражданин",
            "days_ago": 6
        },
        {
            "transcribed_text": "Паркирали коли по тротоарите не позволяват преминаването на майки с колички.",
            "category": "PUBLIC_ORDER",
            "location_mentioned": "Ботевград",
            "urgency": "MEDIUM",
            "formal_letter": "Уважаеми господине/госпожо,\n\nСигнализирам за масово и неправилно паркиране на моторни превозни средства върху тротоарните площи. Това възпрепятства свободното и безопасно придвижване на пешеходци, особено на майки с детски колички и хора с увреждания.\n\nМоля за засилен контрол и налагане на санкции на нарушителите.\n\nС уважение,\nЗагрижен гражданин",
            "days_ago": 7
        }
    ]

    for data in complaints_data:
        mun_info = lookup_municipality(data["location_mentioned"])
        mun_name = mun_info.get("municipality") if mun_info else None
        
        email = get_department_email(data["category"], mun_name)
        
        created_time = datetime.now(timezone.utc) - timedelta(days=data["days_ago"], hours=data.get("hours_ago", 0))

        complaint = Complaint(
            audio_filename=f"mock_audio_{data['days_ago']}.wav",
            transcribed_text=data["transcribed_text"],
            category=data["category"],
            location_mentioned=data["location_mentioned"],
            urgency=data["urgency"],
            formal_letter=data["formal_letter"],
            sent_to_email=email,
            email_sent_successfully=True,
            created_at=created_time
        )
        session.add(complaint)

    session.commit()
    print(f"Successfully added {len(complaints_data)} mock complaints to the database.")

if __name__ == "__main__":
    create_mock_complaints()
