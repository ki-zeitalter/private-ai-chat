import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AssistantsComponent } from './assistants.component';

describe('AppCardsComponent', () => {
  let component: AssistantsComponent;
  let fixture: ComponentFixture<AssistantsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AssistantsComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AssistantsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
