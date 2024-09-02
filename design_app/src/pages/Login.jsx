import React from 'react';
import Toggle from 'react-toggle';
import classNames from 'classnames';
import 'react-toggle/style.css';
import {useState} from 'react';
import AdvancedSearch from '../components/AdvancedSearch';
import AdvancedSearchTips from '../components/AdvancedSearchTips';
import {RadioButtonGroup} from '../../../assets/features/sections/SectionSwitch.tsx';
import {ContentDivider} from 'ui/components/ContentDivider';
//import { useNavigate } from 'react-router-dom';

function Login() { 
    return (
        <div className="nh-login-page__content">
            <div className="login-box">
                <div className="login-box__header">
                    <h3 className="login-box__title">Login to Newshub</h3>
                    {/* <div className="login-logo">
                        <div className="d-flex align-items-center justify-content-center">
                            <img src="/theme/login-logo.svg?h=f8de9868575dd7878f17dcd4a8259195" style="width: 70%;" />
                        </div>
                    </div> */}
                    
                </div>
                <div className="">
                    <form className="form" role="form" id="formLogin">
                        <div className="form-group">
                            <label for="email">Email</label>
                            <input autocomplete="username" className="form-control" id="email" maxlength="64" minlength="1" name="email" required="true" type="text" value="" />
                        </div>
                        <div className="form-group mb-2">
                            <label for="password">Password</label>
                            <input autocomplete="current-password" className="form-control" id="password" name="password" required="true" type="password" value="" />
                        </div>

                        <div className="d-flex align-items-center mb-3 justify-content-between flex-wrap gap-1">
                            <div className="form-check">
                                <input className="form-check-input" id="remember_me" name="remember_me" type="checkbox" value="y" />
                                <label className="form-check-label" for="remember_me">Remember Me</label>
                            </div>
                            <span className='d-flex gap-1 text-md '>
                                <span>Forgot your password?</span>
                                <a className="link" href="/token/reset_password">Click here to reset</a>
                            </span>
                        </div>
                        <button type="submit" className="nh-button nh-button--primary w-100">Login</button>
                    </form>
                </div>

                

                <div className="">
                    <ContentDivider textSize="small" margin="medium">Or</ContentDivider>
                    <form>
                        <button type="submit" title="Login using Single Sign On" className="nh-button nh-button--secondary w-100">Login with company credentials (SSO)</button>
                    </form>
                    <p className='text-muted text-md mt-2'>Note! If your company credentials don't work for login, your company might not have an integration done to this system. Please contact your company IT.</p>
                </div>
                
                <div className="mt-2 mb-3">
                    <div className=" d-flex align-items-center">
                            <span className='d-flex gap-1 text-md '>
                                <span>Don't have an account?</span>
                                <a className="link" href="https://www.thecanadianpress.com/contact/pr-signup">Sign up</a>
                            </span>
                        </div>
                    {/* <ContentDivider textSize="small">Don't have an account?</ContentDivider>
                    <a href="https://www.thecanadianpress.com/contact/pr-signup" className="nh-button nh-button--tertiary w-100 mb-4 ">Sign up</a> */}
                </div>

                
                <div className="">
                    <form className="form" role="form" method="post">
                        <div className="form-group mb-0">
                            <label for="language">Language</label>
                            <div className="field">
                                <select name="locale" className="form-control">
                                    <option value="en" selected="">English</option>
                                    <option value="fr_CA">Français (Canada)</option>
                                </select>
                            </div>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
  }
  
  export default Login;
  