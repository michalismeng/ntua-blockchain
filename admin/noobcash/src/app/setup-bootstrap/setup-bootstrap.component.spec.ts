import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { SetupBootstrapComponent } from './setup-bootstrap.component';

describe('SetupBootstrapComponent', () => {
  let component: SetupBootstrapComponent;
  let fixture: ComponentFixture<SetupBootstrapComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ SetupBootstrapComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(SetupBootstrapComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
