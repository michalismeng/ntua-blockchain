import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { AppState } from '../reducers';
import { Store } from '@ngrx/store';
import { ConfigService } from 'src/services/config.service';
import { filter } from 'rxjs/operators';

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
      'N': ['3', Validators.required],
      'capacity': ['5', Validators.required],
      'difficulty': ['4', Validators.required]
    })
  }

  ngOnInit() {

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
