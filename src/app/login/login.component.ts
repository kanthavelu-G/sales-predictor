import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import {FormControl, Validators} from '@angular/forms';
import { MatSnackBar } from '@angular/material/snack-bar';


@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent implements OnInit {
  hide = true;

  constructor(private router: Router,private _snackBar: MatSnackBar,) { }

  ngOnInit(): void {
  }
  
  do(a:any,b:any){
    if(a==""){
      this._snackBar.open("Enter a Username", "Close", { duration: 3000 });
    }
    else{
      if(b==""){
        this._snackBar.open("Enter a password", "Close", { duration: 3000 });

      }
      else{
        if(a.length<5){
          this._snackBar.open("Username Should Have More Than 5 Character", "Close", { duration: 3000 });
        }
        else{
          if(b.length<5){
            this._snackBar.open("Password Should Have More Than 5 Character", "Close", { duration: 3000 });    
          }
          else{
            this.router.navigate(['file'])
          }
        }
      }
      
    }
    
     
     
  }
  
  
  
}


