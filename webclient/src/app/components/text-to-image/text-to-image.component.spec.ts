import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TextToImageComponent } from './text-to-image.component';

describe('ChatComponent', () => {
  let component: TextToImageComponent;
  let fixture: ComponentFixture<TextToImageComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TextToImageComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(TextToImageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
