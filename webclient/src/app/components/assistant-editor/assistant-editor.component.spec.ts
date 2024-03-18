import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AssistantEditorComponent } from './assistant-editor.component';

describe('AssistantEditorComponent', () => {
  let component: AssistantEditorComponent;
  let fixture: ComponentFixture<AssistantEditorComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AssistantEditorComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(AssistantEditorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
