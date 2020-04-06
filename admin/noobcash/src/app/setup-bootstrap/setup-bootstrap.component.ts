import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ValidatorFn, AbstractControl } from '@angular/forms';
import { AppState } from '../reducers';
import { Store } from '@ngrx/store';
import { ConfigService } from 'src/services/config.service';
import { filter } from 'rxjs/operators';
import { Observable, of } from 'rxjs';

@Component({
  selector: 'app-setup-bootstrap',
  templateUrl: './setup-bootstrap.component.html',
  styleUrls: ['./setup-bootstrap.component.css']
})
export class SetupBootstrapComponent implements OnInit {

  form: FormGroup;

  isLoading = false;

  constructor(
    fb: FormBuilder, 
    private store: Store<AppState>, 
    private configService: ConfigService,
  ) {

    this.form = fb.group({
      'N': ['5', [Validators.required, this.multipleOfFive()]],
      'capacity': ['5', Validators.required],
      'difficulty': ['4', Validators.required]
    })
  }

  ngOnInit() {

  }

  get N() { return this.form.get('N'); }

  get capacity() { return this.form.get('capacity'); }

  get difficulty() { return this.form.get('difficulty'); }

  private multipleOfFive(): ValidatorFn {
    return (control: AbstractControl): {[key: string]: any} | null => {
      const forbidden = control.value % 5 != 0
      return forbidden ? {'forbiddenMultiple': { value: control.value }} : null;
    }
  }

  submit() {
    let value = this.form.value;
    this.isLoading = true;

    this.configService.setupAll(value.N, value.capacity, value.difficulty)
    .subscribe(_ => { 
      this.isLoading = false
    })

    this.store.select(s => s.system.systemState)
      .pipe(filter(s => s == 'up'))
      .subscribe(_ => {
        this.isLoading = false;
      })

  }

}
