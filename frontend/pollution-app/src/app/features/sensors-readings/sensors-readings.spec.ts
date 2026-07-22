import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SensorsReadings } from './sensors-readings';

describe('SensorsReadings', () => {
  let component: SensorsReadings;
  let fixture: ComponentFixture<SensorsReadings>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SensorsReadings]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SensorsReadings);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
