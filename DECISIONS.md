# Decisions

<!-- Fill in each section at the step the activity website gives, then commit and push.
     Write each answer after its label. Keep the headings and labels exactly as they are:
     `python -m analysis` reads them. Limit: 150 words for Before results.
     Fill in Recommendations and Design choice and AI use last, once your app is built. -->

## Before results
For each dataset: positive class; which error matters more for the job (missed positive or false alarm) and why.
- readmission: A missed positive matters more because a patient who will be readmitted gets no extra support, like a follow up call, and may return to hospital unprepared. A false alarm on the other hand costs some time and a call to a patient who didn't even need it.
- diabetes: Once again a missed positive matters more. An adult with diabetes who isn't flagged goes untested and untreated. A false alarm only means a test that came back negative which is cheap.

## Recommendations
- readmission: None is good for this job. Missing a patient who will be readmitted matters more than a false alarm. I would lower the threshold but on the test patients that does not work. Logistic regression at 0.05 flags 95.3% of those readmitted only by flagging 87.8 of every 100 patients and 9.7% of those flagged were readmitted. 
- diabetes: Have Logistic regression set at 0.12 because on the test adults it flagged 90.0% of those with diabetes while flagging 51.7 of every 100 adults. Its test AUROC (0.827) is the highest of the four and close to its training AUROC (0.810), it did not memorise its training patients. The cost is that only 33.1% of flagged adults had diabetes therefore most flags are follow up tests that come back negative.

## Design choice and AI use
A few sentences each. The design choice must be your own idea, not an AI tool's.
- design choice: I decided to put the patients above the chart in section 3 because the brief required the counts. Another design choice I made was to have tabs instead of a two-column layout in section 1. The reason I did that is because only having the 2 columns would've made the page unecessarily long. 
- AI suggestion I turned down: One suggestion the AI made that I turned down was a plain-language summary for Section 2. As I believe there are better ways to get communication across to the viewer/reader. 
