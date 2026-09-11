#þarf að fara betur yfir nöfn á öllum breytum og föllum
import numpy as np

R=8.314 #j*(mol*K)^-1
T_ref=298.15 #K

#veit ekki hvað mér finnst um að hafa dic hér
water_info = {
    "Kh_ref":0.034,
    "H_sol":-19900
}

ethanol_info = {
    "Kh_ref":0.220,
    "H_sol":-10800
}

glucoes_info = {
    "temp_sens_factor":-0.0010, 
    "Ks_ref":0.120
}

def calculate_kH(T,k_ref,H_sol):

    kH_value=k_ref*np.exp((
        H_sol/R
    )*(
        (1/T_ref)-(1/T)
    ))

    return kH_value

def calculate_kH_blend(T,w_water,w_ethanol):

    kH_water=calculate_kH(T,water_info["Kh_ref"],water_info["H_sol"])
    kH_ethanol=calculate_kH(T,ethanol_info["Kh_ref"],ethanol_info["H_sol"])

    kH_blend_value=np.exp(
        w_water*np.log(kH_water)+w_ethanol*np.log(kH_ethanol)
    )

    return kH_blend_value

def calculate_Ks(T,Ks_ref,m):

    Ks=Ks_ref+m*(T-T_ref)

    return Ks

def calculate_kH_final(T,C_glucose,w_water,w_ethanol):

    Ks_value=calculate_Ks(T,glucoes_info["Ks_ref"],glucoes_info["temp_sens_factor"])
    kH_blend_value=calculate_kH_blend(T,w_water,w_ethanol)

    kH_final_value=kH_blend_value*10**(Ks_value*C_glucose)

    return kH_final_value
