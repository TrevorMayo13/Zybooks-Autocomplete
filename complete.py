from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.select import Select
import os
import traceback

drag_and_drop_js = '''
function createEvent(typeOfEvent) {
    var event = document.createEvent("CustomEvent");
    event.initCustomEvent(typeOfEvent, true, true, null);
    event.dataTransfer = {
        data: {},
        setData: function(key, value) {
            this.data[key] = value;
        },
        getData: function(key) {
            return this.data[key];
        }
    };
    return event;
}
function dispatchEvent(element, event, transferData) {
    if (transferData !== undefined) {
        event.dataTransfer = transferData;
    }
    if (element.dispatchEvent) {
        element.dispatchEvent(event);
    } else if (element.fireEvent) {
        element.fireEvent("on" + event.type, event);
    }
}
function simulateHTML5DragAndDrop(element, destination) {
    var dragStartEvent = createEvent('dragstart');
    dispatchEvent(element, dragStartEvent);
    var dropEvent = createEvent('drop');
    dispatchEvent(destination, dropEvent, dragStartEvent.dataTransfer);
    var dragEndEvent = createEvent('dragend');
    dispatchEvent(element, dragEndEvent, dropEvent.dataTransfer);
}
var source = arguments[0];
var destination = arguments[1];
simulateHTML5DragAndDrop(source, destination);
'''

# Enter your zybooks login below with the course code
email = ""#"ExampleEmail@gmail.com"
course = ""#"ExampleCourseCode"

def login(driver, email, course):
    driver.get("https://learn.zybooks.com/signin")
    while (True):
        email_input = driver.find_element(by = By.XPATH, value = "//input[@type='email']")
        password_input = driver.find_element(by = By.XPATH, value = "//input[@type='password']")
        signin_button = driver.find_element(by=By.CLASS_NAME, value="signin-button")
        if not email:
            email = input("Please enter your zyBooks email: ")
        email_input.send_keys(email)
        if (email == "quit"):
            print("--Exiting--")
            driver.quit()
            os._exit(0)

        password = input("Enter your zyBooks password: ")
        #password = "Password123"
        if (password == "quit"):
            print("--Exiting--")
            driver.quit()
            os._exit(0)
        password_input.send_keys(password)

        signin_button.click()
        try:
            driver.implicitly_wait(10)
            driver.implicitly_wait(0)
            break;
        except:
            print("Timed out while authenticating login, aborting...")
            driver.quit()
            os._exit(0)
        if (driver.find_element(By.XPATH, "//button[@disabled='']") or driver.find_element(By.XPATH, 
                "//div[contains(text(), 'Invalid email or password')]")):
            print("--Invalid email or password--\n")
            email_input.clear()
            password_input.clear()
        else:
            print("\nLogin Successful\n")
            break

def selectzyBook(driver):
    global course
    while (True):
        if not course:
            course = input("Enter your course ID or the name of your course: ")
        if (course == "quit"):
            print("--Exiting--")
            driver.quit()
            os._exit(0)
        try:
            course = course.replace(" ", "")
            zybook_selection = driver.find_element(By.XPATH, "//a[contains(@href, '" + course + "')]")
            zybook_selection.click()
            break
        except:
            print("--Invalid course--\n")
    print("zyBook Selected\n")


def chapterSelection(driver):
    while (True):
        open_chapters = driver.find_elements(By.CSS_SELECTOR, 
            "li.toc-item.chapter-item.js-draggableObject.draggable-object.expanded.ember-view")
        for open_chapter in open_chapters:
            open_chapter.find_element(By.CSS_SELECTOR, "div.chapter-info.unused").click()
        chapter = input("Enter the chapter number you want completed: ")
        if (chapter == "quit"):
            print("--Exiting--")
            driver.quit()
            os._exit(0)
        try:
            chapter_selection = driver.find_elements(By.XPATH, 
                "//*[contains(@class, 'table-of-contents-list')]/*[contains(@class, 'chapter-item')]")[int(chapter) - 1]
            chapter_selection.click()
            print("Chapter Selected\n")
            return chapter
        except:
            print("--Invalid chapter--\n")


def sectionSelection(driver, chapter):
    while (True):
        chapter_selection = driver.find_elements(By.XPATH, 
            "//*[contains(@class, 'table-of-contents-list')]/*[contains(@class, 'chapter-item')]")[int(chapter) - 1]
        section_selection = input(
            "Enter the section number you want completed. Enter \"all\" if you would like the entire chapter completed: ")
        if (section_selection == "quit"):
            print("--Exiting--")
            driver.quit()
            os._exit(0)
        if (section_selection.isnumeric()):
            #//span[@class='section-item']
            section_button = chapter_selection.find_elements(By.CLASS_NAME, "section-title-link")[
                int(section_selection) - 1]
            section_button.click()
            print("\nStarting chapter " + chapter + " section " + section_selection + "...")
            try:
                WebDriverWait(driver, 10).until(expected_conditions.element_to_be_clickable(
                    (By.CSS_SELECTOR, ".zybook-section.zb-card.ember-view")))
            except:
                print(
                    "Timed out while loading chapter " + chapter + " section " + section_selection + " content, aborting...")
                driver.quit()
                os._exit(0)
            completeParticipationActivities(driver)
            try:
                driver.find_element(By.XPATH, "/html/body/div[4]/header/div[1]/div/ul/a[2]").click()
            except NoSuchElementException:
                driver.find_element(By.XPATH, "/html/body/div[3]/header/div[1]/div/ul/a[2]").click()
            break
        elif (section_selection == "all"):
            sections = chapter_selection.find_elements(By.CLASS_NAME, "section-title-link")
            sections[0].click()
            for section_index in range(len(sections)):
                print("\nStarting chapter " + chapter + " section " + str(section_index + 1) + "...")
                try:
                    WebDriverWait(driver, 10).until(expected_conditions.element_to_be_clickable(
                        (By.CSS_SELECTOR, ".zybook-section.zb-card.ember-view")))
                except:
                    print("Timed out while loading chapter " + chapter + " section " + section_selection + " content, aborting...")
                    driver.quit()
                    os._exit(0)
                completeParticipationActivities(driver)
                if (section_index != (len(sections) - 1)):
                    driver.find_element(By.CSS_SELECTOR, "nav.section-nav.next > a.ember-view.nav-link").click()
            try:
                driver.find_element(By.XPATH, "/html/body/div[4]/header/div[1]/div/ul/a[2]").click()
            except NoSuchElementException:
                driver.find_element(By.XPATH, "/html/body/div[3]/header/div[1]/div/ul/a[2]").click()
            break
        else:
            print("Please enter a valid section number.")


def completeParticipationActivities(driver):
    try:
        playAnimations(driver)
        completeCustomInteractions(driver)
        completeMultipleChoice(driver)
        completeShortAnswer(driver)
        completeMatching(driver)
        completeSelectionProblems(driver)

    except (NoSuchElementException, TimeoutException):
        pass

def checkCompleted(activity):
    if skip_completed:
        try:
            activity.find_element(By.CSS_SELECTOR, 
                "div.zb-chevron.check.title-bar-chevron.orange.filled.large")
            return True
        except NoSuchElementException:
            return False
    return False


def playAnimations(driver):
    animation_players = driver.find_elements(By.CSS_SELECTOR, 
        "div.interactive-activity-container.animation-player-content-resource.participation.large.ember-view")
    animation_players += driver.find_elements(By.CSS_SELECTOR, 
        "div.interactive-activity-container.animation-player-content-resource.participation.medium.ember-view")
    animation_players += driver.find_elements(By.CSS_SELECTOR, 
        "div.interactive-activity-container.animation-player-content-resource.participation.small.ember-view")
    for animation in animation_players:
        if checkCompleted(animation):
            print("Skipping completed animation activity")
            continue
        # crumbs = driver.find_element(By.CSS_SELECTOR, "li.bread-crumb")
        start = driver.find_element(By.CSS_SELECTOR, "div.section-header-row")
        try:
            start.click()
        except ElementClickInterceptedError:
            pass
        #webdriver.ActionChains(driver).move_to_element(start).click().perform()
        double_speed = animation.find_element(By.CSS_SELECTOR, "div.speed-control")
        double_speed.click()
        start_button = animation.find_element(By.CSS_SELECTOR, "button.zb-button.primary.raised.start-button.start-graphic")
        start_button.click()
        while (True):
            if (animation.find_elements(By.XPATH, ".//div[@class='pause-button']")):
                continue
            try:
                play_button = animation.find_element(By.CSS_SELECTOR, "div.play-button.bounce")
                play_button.click()
            except:
                pass
            if (animation.find_elements(By.CSS_SELECTOR, "div.play-button.rotate-180")):
                break
        print("Completed animation activity")


def completeCustomInteractions(driver):
    custom_activties = driver.find_elements(By.XPATH, 
        "//div[@class='interactive-activity-container custom-content-resource participation large ember-view']")
    custom_activties += driver.find_elements(By.XPATH, 
        "//div[@class='interactive-activity-container custom-content-resource participation medium ember-view']")
    custom_activties += driver.find_elements(By.XPATH, 
        "//div[@class='interactive-activity-container custom-content-resource participation small ember-view']")
    for activity in custom_activties:
        if checkCompleted(activity):
            print("Skipping completed interactive activity")
            continue
        start = driver.find_element(By.XPATH, "//div[@class='section-header-row']")
        try:
            start.click()
        except ElementClickInterceptedError:
            pass
        #webdriver.ActionChains(driver).move_to_element(start).click().perform()
        buttons = activity.find_elements(By.XPATH, ".//button[@class='button']")
        for button in buttons:
            button.click()


def completeMultipleChoice(driver):
    multiple_choice_sets = driver.find_elements(By.XPATH, 
        "//div[@class='interactive-activity-container multiple-choice-content-resource participation large ember-view']")
    multiple_choice_sets += driver.find_elements(By.XPATH, 
        "//div[@class='interactive-activity-container multiple-choice-content-resource participation medium ember-view']")
    multiple_choice_sets += driver.find_elements(By.XPATH, 
        "//div[@class='interactive-activity-container multiple-choice-content-resource participation small ember-view']")
    for question_set in multiple_choice_sets:
        if checkCompleted(question_set):
            print("Skipping completed multiple choice activity")
            continue
        start = driver.find_element(By.XPATH, "//div[@class='section-header-row']")
        try:
            start.click()
        except ElementClickInterceptedError:
            pass
        #webdriver.ActionChains(driver).move_to_element(start).click().perform()
        questions = question_set.find_elements(By.XPATH, 
            ".//div[@class='question-set-question multiple-choice-question ember-view']")
        for question in questions:
            if (question.find_elements(By.XPATH, ".//div[@class='explanation has-explanation correct']")):
                break
            choices = question.find_elements(By.XPATH, ".//label[@aria-hidden='true']")
            for choice in choices:
                choice.click()
                if (question.find_elements(By.XPATH, ".//div[@class='explanation has-explanation correct']")):
                    break
        print("Completed multiple choice set")


def completeShortAnswer(driver):
    short_answer_sets = driver.find_elements(By.XPATH, 
        "//div[@class='interactive-activity-container short-answer-content-resource participation large ember-view']")
    short_answer_sets += driver.find_elements(By.XPATH, 
        "//div[@class='interactive-activity-container short-answer-content-resource participation medium ember-view']")
    short_answer_sets += driver.find_elements(By.XPATH, 
        "//div[@class='interactive-activity-container short-answer-content-resource participation small ember-view']")
    print("attempting short answer")
    i = 0
    for question_set in short_answer_sets:
        i+=1
        print(i)
        if checkCompleted(question_set):
            print("Skipping completed short answer activity")
            continue
        start = driver.find_element(By.XPATH, "//div[@class='section-header-row']")
        try:
            start.click()
        except ElementClickInterceptedError:
            pass
        #webdriver.ActionChains(driver).move_to_element(start).click().perform()
        questions = question_set.find_elements(By.XPATH, 
            ".//div[@class='question-set-question short-answer-question ember-view']")
        for question in questions:
            show_answer_button = question.find_element(By.CSS_SELECTOR, 
                "button.zb-button.secondary.show-answer-button")
            show_answer_button.click()
            show_answer_button.click()
            answer = question.find_element(By.XPATH, ".//span[@class='forfeit-answer ']").text
            text_area = question.find_element(By.CSS_SELECTOR, 
                "textarea.ember-text-area.ember-view.zb-text-area.hide-scrollbar")
            text_area.send_keys(answer)
            check_button = question.find_element(By.CSS_SELECTOR, 
                "button.zb-button.primary.check-button")
            check_button.click()
        print("Completed short answer set")


def completeMatching(driver):
    matching_sets = driver.find_elements(By.XPATH, 
        "//div[@class='interactive-activity-container custom-content-resource participation large ember-view']")
    matching_sets += driver.find_elements(By.XPATH, 
        "//div[@class='interactive-activity-container custom-content-resource participation medium ember-view']")
    matching_sets += driver.find_elements(By.XPATH, 
        "//div[@class='interactive-activity-container custom-content-resource participation small ember-view']")
    for matching in matching_sets:
        if checkCompleted(matching):
            print("Skipping completed matching/run activity")
            continue
        try:  # Support for 'run this code' activities, which use same class definition as matching activities. Only works for some code activities, as some require just running while others require editing the code first
            run_button = matching.find_element(By.CSS_SELECTOR, "button.run-button.zb-button.primary.raised")
            run_button.click()
            print("Attempted run activity")
            continue
        except NoSuchElementException:
            pass

        matching.click()
        rows = matching.find_elements(By.CLASS_NAME, "definition-row")

        class row_is_correct(object):
            def __init__(self, row):
                self.row = row

            def __call__(self, driver):
                if self.row.text.endswith("Correct"):
                    return True
                else:
                    return False

        for row in rows:
            row_correct = False
            while not row_correct:
                choice = matching.find_element(By.CLASS_NAME, "draggable-object")
                bucket = row.find_element(By.CLASS_NAME, "term-bucket")
                driver.execute_script(drag_and_drop_js, choice, bucket)
                try:
                    WebDriverWait(row, .75).until(row_is_correct(row))  # Lowering delay causes issues
                    row_correct = True
                except TimeoutException:
                    pass
        print("Completed matching set")


def completeSelectionProblems(driver):
    selection_problem_sets = driver.find_elements(By.XPATH, 
        "//div[@class='interactive-activity-container detect-answer-content-resource participation large ember-view']")
    selection_problem_sets += driver.find_elements(By.XPATH, 
        "//div[@class='interactive-activity-container detect-answer-content-resource participation medium ember-view']")
    selection_problem_sets += driver.find_elements(By.XPATH, 
        "//div[@class='interactive-activity-container detect-answer-content-resource participation small ember-view']")
    for question_set in selection_problem_sets:
        if checkCompleted(question_set):
            print("Skipping completed selection activity")
            continue
        start = driver.find_element(By.XPATH, "//div[@class='section-header-row']")
        try:
            start.click()
        except ElementClickInterceptedError:
            pass
        #webdriver.ActionChains(driver).move_to_element(start).click().perform()
        questions = question_set.find_elements(By.XPATH, 
            ".//div[@class='question-set-question detect-answer-question ember-view']")
        for question in questions:
            choices = question.find_elements(By.XPATH, ".//div[@class='unclicked']")
            for choice in choices:
                choice.click()
                if (question.find_elements(By.XPATH, ".//div[@class='explanation has-explanation correct']")):
                    break
        print("Completed selection problem set")


def completeProgressionChallenges(driver):  # Currently not used
    progression_challenges = driver.find_elements(By.XPATH, 
        "//div[@class='interactive-activity-container custom-content-resource challenge large ember-view']")
    progression_challenges += driver.find_elements(By.XPATH, 
        "//div[@class='interactive-activity-container custom-content-resource challenge medium ember-view']")
    progression_challenges += driver.find_elements(By.XPATH, 
        "//div[@class='interactive-activity-container custom-content-resource challenge small ember-view']")
    for progression in progression_challenges:
        if checkCompleted(progression):
            print("Skipping completed progression activity")
            continue
        progression_status = progression.find_elements(By.XPATH, ".//div[@class='zyante-progression-status-bar'']/div")
        for status in progression_status:
            if status.text == 1:
                start_button = progression.find_element(By.XPATH, 
                    ".//button[@class='zyante-progression-start-button button']")
                start_button.click()
            else:
                next_button = progression.find_element(By.XPATH, "class='zyante-progression-next-button button']")
                next_button.click()
    return


if (os.name == 'nt'):
    geckodriver_path = '.\\geckodriver.exe'
else:
    geckodriver_path = './geckodriver'
options = Options()
options.headless = True
skip_completed = True
# browser = input("Choose the web browser you have installed:\n") #todo: give options for different installed browsers
s = Service(geckodriver_path)
op = webdriver.FirefoxOptions()
driver = webdriver.Firefox(service = s, options = op)
print("\nTo exit the script, enter \"quit\" at any prompt.")
print("\nHeadless Firefox browswer initiated.\n")



try:
    login(driver, email, course)
    try:
        WebDriverWait(driver, 10).until(expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, ".library-page")))
    except:
        print("Timed out while loading zyBooks library, aborting...")
        driver.quit()
        os._exit(0)
    selectzyBook(driver)
    try:
        WebDriverWait(driver, 10).until(
            expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, ".table-of-contents.ember-view")))
    except:
        print("Timed out while loading zyBook table of contents, aborting...")
        driver.quit()
        os._exit(0)
    while (True):
        chapter = chapterSelection(driver)
        try:
            WebDriverWait(driver, 10).until(
                expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, ".section-list")))
        except:
            print("Timed out while loading zyBook list of sections, aborting...")
            driver.quit()
            os._exit(0)
        sectionSelection(driver, chapter)
        print("Participation activities completed.\n")
except Exception as e:
    print(e)
    with open("exception.log", "w") as log:
        traceback.print_exc(file=log)
        log.write("\n")
        log.write("#" * 80)
        log.write("\n")
        log.write(driver.page_source)

driver.quit()
print("Headless Firefox browser closed")
